from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, StudentConversationSerializer
from api.permissions import IsAdmin, IsStudent
from students.models import Student

class ConversationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    ViewSet for managing conversations.
    - Admins can list and retrieve all conversations.
    - Students can list/retrieve only their own conversation.
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        # Admin gets a list serializer
        if self.request.user.is_staff:
            return ConversationSerializer
        # Student gets a detailed serializer with messages
        return StudentConversationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            # Admins see all conversations, ordered by most recent message
            return Conversation.objects.select_related("student__user").order_by('-last_message_at')
        
        # Students only see their own conversation
        try:
            student = user.student
            return Conversation.objects.filter(student=student).prefetch_related("messages")
        except Student.DoesNotExist:
            return Conversation.objects.none()

    @action(detail=False, methods=['get'], url_path='my-conversation')
    def my_conversation(self, request):
        """
        A specific endpoint for students to get or create their conversation.
        """
        
        # --- THIS IS THE FIX ---
        # Changed `request.user.is_student` to `request.user.is_staff`
        if request.user.is_staff:
             return Response({"detail": "Only students can access this."}, status=status.HTTP_403_FORBIDDEN)
        # --- END FIX ---
        
        try:
            student = request.user.student
        except Student.DoesNotExist:
             return Response({"detail": "Student profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Get or create the conversation
        conversation, created = Conversation.objects.get_or_create(student=student)
        
        # When student views it, mark as read for them
        conversation.mark_as_read_by(request.user)
        
        serializer = StudentConversationSerializer(conversation, context={'request': request})
        return Response(serializer.data)


class MessageViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin):
    """
    ViewSet for listing and creating messages within a conversation.
    Accessed via /api/v1/conversations/<conversation_pk>/messages/
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_conversation(self):
        """
        Helper to get the parent conversation and check permissions.
        """
        conversation_id = self.kwargs.get('conversation_pk')
        user = self.request.user
        
        try:
            conversation = Conversation.objects.get(pk=conversation_id)
        except Conversation.DoesNotExist:
            return None
            
        # Security check: User must be an admin OR the student in this conversation
        if user.is_staff or conversation.student.user == user:
            return conversation
        
        return None

    def get_queryset(self):
        conversation = self.get_conversation()
        if conversation:
            # Mark as read when messages are listed
            conversation.mark_as_read_by(self.request.user)
            return conversation.messages.select_related('sender').order_by('sent_at')
        return Message.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['conversation'] = self.get_conversation()
        return context

    def create(self, request, *args, **kwargs):
        conversation = self.get_conversation()
        if not conversation:
            return Response({"detail": "Conversation not found or access denied."}, status=status.HTTP_404_NOT_FOUND)
        
        return super().create(request, *args, **kwargs)
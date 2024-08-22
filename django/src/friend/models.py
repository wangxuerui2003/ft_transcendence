from datetime import timezone
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserRelation(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_relations")
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend_relations", default=None)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(auto_now=True)
    blocked = models.BooleanField(default=False)
    blocked_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.friend.username}"
    
    def delete(self):
        self.deleted = True
        self.deleted_at = timezone.now()
        self.save()
        
    def block(self):
        self.blocked = True
        self.blocked_at = timezone.now()
        self.save()
    
    def unblock(self):
        self.blocked = False
        self.save()


class FriendRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'P', 'Pending'
        ACCEPTED = 'A', 'Accepted'
        REJECTED = 'R', 'Rejected'

    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_requests")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend_requests", default=None)
    status = models.CharField(max_length=1, choices=Status.choices, default=Status.PENDING)
    sender_words = models.TextField(blank=True)
    reject_reason = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}"
    
    def accept(self, current_user):
        if current_user == self.sender:
            raise ValueError("You cannot accept your own request.")
        self.status = self.Status.ACCEPTED
        self.save()
        
    def reject(self, current_user, reject_reason=""):
        if current_user == self.sender:
            raise ValueError("You cannot reject your own request.")
        self.status = self.Status.REJECTED
        self.reject_reason = reject_reason
        self.save()
    
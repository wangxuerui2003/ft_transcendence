# models.py
from django.db import models
from django.contrib.auth import get_user_model
from base.models import BaseModel
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from datetime import timedelta
from django.utils import timezone


User = get_user_model()


class Player(BaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="player",
    )
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    elo = models.IntegerField(default=1200)

    def __str__(self):
        return f"{self.user.username}"


class Match(BaseModel):
    class MatchType(models.TextChoices):
        PVP = "P", "PVP"
        PVE = "E", "PVE"

    winner = models.ForeignKey(
        Player, on_delete=models.SET_NULL, null=True, related_name="match_winner"
    )
    loser = models.ForeignKey(
        Player, on_delete=models.SET_NULL, null=True, related_name="match_loser"
    )
    winner_score = models.IntegerField(default=0)
    loser_score = models.IntegerField(default=0)
    type = models.CharField(
        max_length=1, choices=MatchType.choices, null=True, blank=True, default=MatchType.PVP
    )
    ended_at = models.DateTimeField(null=True, blank=True)
    history = GenericRelation("MatchHistory", related_query_name="match_history")

    def __str__(self):
        return f"{self.winner} vs {self.loser}. winner: {self.winner}"


class TournamentRoom(BaseModel):
    MAX_PLAYERS = 8

    class Status(models.TextChoices):
        WAITING = "W", "Waiting"
        ONGOING = "O", "Ongoing"
        COMPLETED = "C", "Completed"

    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    players = models.ManyToManyField(
        "TournamentPlayer", related_name="tournament_players"
    )
    players_left = models.ManyToManyField(
        "TournamentPlayer", related_name="tournament_players_left"
    )
    winner = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        related_name="tournament_winner",
        null=True,
        blank=True,
    )
    matches = models.ManyToManyField(
        "TournamentMatch", related_name="tournament_matches"
    )
    status = models.CharField(
        max_length=1, choices=Status.choices, default=Status.WAITING
    )
    ended_at = models.DateTimeField(null=True, blank=True)
    history = GenericRelation("MatchHistory", related_query_name="tournament_history")

    def save(self, *args, **kwargs):
        if self.players.count() >= self.MAX_PLAYERS:
            raise ValueError("Maximum number of players exceeded.")
        super().save(*args, **kwargs)

    def add_player(self, user):
        if self.players.count() >= self.MAX_PLAYERS:
            raise ValueError("Maximum number of players exceeded.")
        try:
            player = Player.objects.get(user=user)
            tournament_player = TournamentPlayer.objects.create(
                player=player, tournament=self
            )
        except (Player.DoesNotExist, TournamentPlayer.DoesNotExist):
            raise ValueError("Player or TournamentPlayer does not exist.")
        self.players.add(tournament_player)
        self.save()

    def remove_player(self, user):
        try:
            player = Player.objects.get(user=user)
            tournament_player = TournamentPlayer.objects.get(
                player=player, tournament=self
            )
        except (Player.DoesNotExist, TournamentPlayer.DoesNotExist):
            raise ValueError("Player or TournamentPlayer does not exist.")
        self.players.remove(tournament_player)
        tournament_player.delete()
        self.save()

    def is_member(self, user):
        try:
            player = Player.objects.get(user=user)
            return TournamentPlayer.objects.filter(
                player=player, tournament=self
            ).exists()
        except (Player.DoesNotExist, TournamentPlayer.DoesNotExist):
            return False

    def is_owner(self, user):
        return self.owner == user

    def start(self):
        if not self.is_owner(self.owner.user):
            raise ValueError("You are not the owner of this tournament room.")
        if self.players.count() < 4:
            raise ValueError("Minimum number of players not met.")
        if self.players.count() % 2 != 0:
            raise ValueError("Number of players must be even.")
        if self.status != self.Status.WAITING:
            raise ValueError("Tournament is not waiting.")
        self.players_left.set(self.players.all())
        self.status = self.Status.ONGOING
        self.save()

    def next_match(self):
        if self.status != self.Status.ONGOING:
            raise ValueError("Tournament is not ongoing.")
        if self.players_left.count() == 0:
            raise ValueError("No players left.")
        if self.players_left.count() == 1:
            self.winner = self.players_left.first().player
            self.save()
            return None, False # winner is found
        is_next_round = False
        if self.matches.filter(status=TournamentMatch.Status.WAITING).count() == 0:
            self.__next_round()
            is_next_round = True
        matches = self.matches.filter(status=TournamentMatch.Status.WAITING).order_by('-created_at')
        match = matches.first()
        match.status = TournamentMatch.Status.ONGOING
        match.save()
        return match, is_next_round

    def __next_round(self):
        if self.status != self.Status.ONGOING:
            raise ValueError("Tournament is not ongoing.")
        if self.matches.filter(status=TournamentMatch.Status.ONGOING).count() > 0:
            raise ValueError("There is an ongoing match.")
        players_left = list(self.players_left.all())
        for i in range(0, len(players_left), 2):
            match = TournamentMatch.objects.create(tournament=self)
            match.winner = players_left[i]
            match.loser = players_left[i + 1]
            match.save()
            self.matches.add(match)

    def end(self):
        self.status = self.Status.COMPLETED
        self.save()

    def __str__(self):
        return f"Tournament: {self.name}"


class TournamentPlayer(BaseModel):
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="tournament_player"
    )
    tournament = models.ForeignKey(
        TournamentRoom, on_delete=models.CASCADE, related_name="tournament_player"
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Player {self.player} in {self.tournament}"


class TournamentMatch(BaseModel):
    class Status(models.TextChoices):
        WAITING = "W", "Waiting"
        ONGOING = "O", "Ongoing"
        COMPLETED = "C", "Completed"

    status = models.CharField(choices=Status.choices, default=Status.WAITING, max_length=1)
    winner = models.ForeignKey(
        TournamentPlayer,
        on_delete=models.SET_NULL,
        related_name="tournament_match_winner",
        null=True,
        blank=True,
    )
    loser = models.ForeignKey(
        TournamentPlayer,
        on_delete=models.SET_NULL,
        related_name="tournament_match_loser",
        null=True,
        blank=True,
    )
    winner_score = models.IntegerField(default=0)
    loser_score = models.IntegerField(default=0)
    tournament = models.ForeignKey(
        TournamentRoom, on_delete=models.CASCADE, related_name="tournament_match"
    )

    def __str__(self):
        return f"{self.winner} vs {self.loser}. winner: {self.winner}"


class MatchHistory(BaseModel):
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="match_history_player"
    )
    match = models.ForeignKey(
        Match, on_delete=models.CASCADE, related_name="match_history_match"
    )
    elo_change = models.IntegerField(default=0)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return f"{self.player} in {self.match}. Elo change: {self.elo_change}"


class UserActiveTournament(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="active_tournament")
    tournament = models.ForeignKey(TournamentRoom, on_delete=models.SET_NULL, null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.user} in {self.tournament}"
    

class MatchInvitation(BaseModel):
    INVITATION_EXPIRE_TIME = 60 * 5  # in seconds, 5 minutes
    class Status(models.TextChoices):
        WAITING = "W", "Waiting"
        ACCEPTED = "A", "Accepted"
        REJECTED = "R", "Rejected"

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")
    status = models.CharField(choices=Status.choices, default=Status.WAITING, max_length=1)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, null=True, related_name="invitation_match")
    expired_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"From {self.sender} to {self.receiver}. Match: {self.match}"
    
    def save(self, *args, **kwargs):
        if self.status == self.Status.WAITING and not self.expired_at:
            self.expired_at = timezone.now() + timedelta(seconds=self.INVITATION_EXPIRE_TIME)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return self.expired_at < timezone.now()
    
    def accept(self):
        if self.status != self.Status.WAITING:
            raise ValueError("Invitation is not waiting.")
        self.status = self.Status.ACCEPTED
        self.expired_at = None
        self.save()
        
    def reject(self):
        if self.status != self.Status.WAITING:
            raise ValueError("Invitation is not waiting.")
        self.status = self.Status.REJECTED
        self.expired_at = None
        self.save()
        
    def create_match(self):
        if self.status != self.Status.ACCEPTED:
            raise ValueError("Invitation is not accepted.")
        if self.match:
            raise ValueError("Match already exists.")
        match = Match.objects.create(
            winner=self.sender.player,
            loser=self.receiver.player,
            type=Match.MatchType.PVP
        )
        self.match = match
        self.save()
        return match

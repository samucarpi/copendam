from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Poll(models.Model):
    """Modello per il sondaggio principale"""
    
    POLL_TYPES = [
        ('single', 'Scelta singola'),
        ('multiple', 'Scelta multipla'),
        ('rating', 'Valutazione (1-5)'),
        ('text', 'Risposta aperta'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Bozza'),
        ('active', 'Attivo'),
        ('closed', 'Chiuso'),
        ('archived', 'Archiviato'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Titolo del sondaggio")
    description = models.TextField(blank=True, verbose_name="Descrizione")
    poll_type = models.CharField(
        max_length=10, 
        choices=POLL_TYPES, 
        default='single',
        verbose_name="Tipo di sondaggio"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Stato"
    )
    
    # Date fields
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creato il")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Aggiornato il")
    start_date = models.DateTimeField(
        default=timezone.now, 
        verbose_name="Data di inizio"
    )
    end_date = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="Data di fine"
    )
    
    # User fields
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_polls',
        verbose_name="Creato da"
    )
    
    # Settings
    is_anonymous = models.BooleanField(
        default=False,
        verbose_name="Risposte anonime"
    )
    allow_multiple_responses = models.BooleanField(
        default=False,
        verbose_name="Permetti risposte multiple"
    )
    show_results = models.BooleanField(
        default=True,
        verbose_name="Mostra risultati"
    )
    
    class Meta:
        verbose_name = "Sondaggio"
        verbose_name_plural = "Sondaggi"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def is_active(self):
        """Verifica se il sondaggio è attivo"""
        now = timezone.now()
        return (
            self.status == 'active' and
            self.start_date <= now and
            (self.end_date is None or self.end_date >= now)
        )
    
    @property
    def total_responses(self):
        """Conta il numero totale di risposte"""
        return self.responses.count()
    
    def get_results(self):
        """Restituisce i risultati del sondaggio"""
        results = {}
        for question in self.questions.all():
            results[question.id] = question.get_results()
        return results


class Question(models.Model):
    """Modello per le domande del sondaggio"""
    
    QUESTION_TYPES = [
        ('single_choice', 'Scelta singola'),
        ('multiple_choice', 'Scelta multipla'),
        ('rating', 'Valutazione'),
        ('text', 'Testo libero'),
        ('number', 'Numero'),
        ('date', 'Data'),
    ]
    
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="Sondaggio"
    )
    text = models.TextField(verbose_name="Testo della domanda")
    question_type = models.CharField(
        max_length=15,
        choices=QUESTION_TYPES,
        default='single_choice',
        verbose_name="Tipo di domanda"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Ordine")
    is_required = models.BooleanField(default=True, verbose_name="Obbligatoria")
    
    # Per domande di tipo rating
    min_rating = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Valutazione minima"
    )
    max_rating = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Valutazione massima"
    )
    
    class Meta:
        verbose_name = "Domanda"
        verbose_name_plural = "Domande"
        ordering = ['poll', 'order']
        unique_together = ['poll', 'order']
    
    def __str__(self):
        return f"{self.poll.title} - {self.text[:50]}"
    
    def get_results(self):
        """Restituisce i risultati per questa domanda"""
        if self.question_type in ['single_choice', 'multiple_choice']:
            results = {}
            for choice in self.choices.all():
                count = choice.responses.count()
                results[choice.text] = count
            return results
        elif self.question_type == 'rating':
            responses = self.responses.values_list('rating_value', flat=True)
            if responses:
                avg_rating = sum(responses) / len(responses)
                return {
                    'average': round(avg_rating, 2),
                    'total_responses': len(responses),
                    'distribution': dict(zip(
                        range(self.min_rating, self.max_rating + 1),
                        [list(responses).count(i) for i in range(self.min_rating, self.max_rating + 1)]
                    ))
                }
            return {'average': 0, 'total_responses': 0, 'distribution': {}}
        else:
            # Per domande aperte
            return {
                'total_responses': self.responses.count(),
                'responses': list(self.responses.values_list('text_value', flat=True))
            }


class Choice(models.Model):
    """Modello per le scelte delle domande"""
    
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name="Domanda"
    )
    text = models.CharField(max_length=200, verbose_name="Testo della scelta")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordine")
    
    class Meta:
        verbose_name = "Scelta"
        verbose_name_plural = "Scelte"
        ordering = ['question', 'order']
        unique_together = ['question', 'order']
    
    def __str__(self):
        return f"{self.question.text[:30]} - {self.text}"


class Response(models.Model):
    """Modello per le risposte al sondaggio"""
    
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name="Sondaggio"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='poll_responses',
        verbose_name="Utente"
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name="Chiave sessione"
    )
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Inviato il")
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Indirizzo IP"
    )
    
    class Meta:
        verbose_name = "Risposta"
        verbose_name_plural = "Risposte"
        ordering = ['-submitted_at']
        # Un utente può rispondere solo una volta per sondaggio (se non anonimo)
        unique_together = ['poll', 'user']
    
    def __str__(self):
        user_info = self.user.username if self.user else f"Anonimo ({self.session_key[:8]})"
        return f"{self.poll.title} - {user_info}"


class Answer(models.Model):
    """Modello per le singole risposte alle domande"""
    
    response = models.ForeignKey(
        Response,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="Risposta"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name="Domanda"
    )
    
    # Campi per diversi tipi di risposta
    selected_choices = models.ManyToManyField(
        Choice,
        blank=True,
        related_name='responses',
        verbose_name="Scelte selezionate"
    )
    text_value = models.TextField(
        null=True,
        blank=True,
        verbose_name="Valore testuale"
    )
    number_value = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Valore numerico"
    )
    date_value = models.DateField(
        null=True,
        blank=True,
        verbose_name="Valore data"
    )
    rating_value = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Valore valutazione"
    )
    
    class Meta:
        verbose_name = "Risposta alla domanda"
        verbose_name_plural = "Risposte alle domande"
        unique_together = ['response', 'question']
    
    def __str__(self):
        return f"{self.response} - {self.question.text[:30]}"
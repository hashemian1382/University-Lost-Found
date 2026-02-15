# backend/interactions/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Report, Comment
from core.models import Item

@receiver(post_save, sender=Report)
def check_report_threshold(sender, instance, created, **kwargs):
    if created:
        content_type = instance.content_type
        object_id = instance.object_id
        
        report_count = Report.objects.filter(
            content_type=content_type, 
            object_id=object_id
        ).count()

        if report_count >= 5:
            model_class = content_type.model_class()
            try:
                obj = model_class.objects.get(id=object_id)
                
                if isinstance(obj, Item):
                    if obj.status != 'DELETED':
                        obj.status = 'DELETED'
                        obj.save()
                
                elif isinstance(obj, Comment):
                    hidden_text = "[This comment has been hidden due to reports]"
                    if obj.text != hidden_text:
                        obj.text = hidden_text
                        obj.save()
            except model_class.DoesNotExist:
                pass

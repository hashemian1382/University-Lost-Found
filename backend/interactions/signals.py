from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Report
from core.models import Item
from .models import Comment

@receiver(post_save, sender=Report)
def check_report_threshold(sender, instance, created, **kwargs):
    if created:
        content_type = instance.content_type
        object_id = instance.object_id
        
        # Count reports for this object
        report_count = Report.objects.filter(
            content_type=content_type, 
            object_id=object_id
        ).count()

        if report_count >= 5:
            model_class = content_type.model_class()
            obj = model_class.objects.get(id=object_id)
            
            if isinstance(obj, Item):
                obj.status = 'DELETED' # Or a specific 'HIDDEN' status
                obj.save()
            elif isinstance(obj, Comment):
                obj.text = "[This comment has been hidden due to reports]"
                obj.save()
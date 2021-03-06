from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models
from django.contrib.auth.models import User
from datetime import date


class Exposure(models.Model):
    """Exposure information"""

    # TODO: make null=False when exposure data is available

    exposure_id = models.IntegerField(
        primary_key=True,
        help_text='Exposure number'
    )
    telra = models.FloatField(
        blank=True, null=True,
        help_text='Central RA of the exposure'
    )
    teldec = models.FloatField(
        blank=True, null=True,
        help_text='Central Dec of the exposure'
    )
    tile = models.IntegerField(
        blank=True, null=True,
        help_text='Tile ID'
    )
    dateobs = models.DateTimeField(
        help_text='Date of observation'
    )
    flavor = models.CharField(
        max_length=45,
        default='Object',
        help_text='Type of observation'
    )
    night = models.CharField(
        max_length=45,
        help_text='Night ID',
        db_index=True
        )
    airmass = models.FloatField(
        blank=True, null=True,
        help_text='Airmass'
    )
    program = models.CharField(
        max_length=45,
        blank=True, null=True,
        help_text='Program'
    )
    exptime = models.FloatField(
        blank=True, null=True,
        help_text='Exposure time'
    )


class Configuration(models.Model):
    """Configuration information"""

    name = models.CharField(
        max_length=45, default='QLF',
        help_text='Name of the configuration.',
        primary_key=True
    )
    configuration = JSONField(
        default={},
        help_text='Configuration used.'
    )
    creation_date = models.DateTimeField(
        auto_now=True,
        help_text='Datetime when the configuration was created'
    )


class Process(models.Model):
    """Process information"""

    STATUS_OK = 0
    STATUS_FAILED = 1

    pipeline_name = models.CharField(
        max_length=60,
        help_text='Name of the pipeline.'
    )
    process_dir = models.CharField(
        max_length=145,
        help_text='Path to process'
    )
    version = models.CharField(
        max_length=45,
        help_text='Path to process'
    )
    start = models.DateTimeField(
        auto_now=True,
        help_text='Datetime when the process was started'
    )
    end = models.DateTimeField(
        blank=True, null=True,
        help_text='Datetime when the process was finished.'
    )
    status = models.SmallIntegerField(
        default=STATUS_OK,
        help_text='Process status, 0=OK, 1=Failed'
    )
    exposure = models.ForeignKey(
        Exposure,
        related_name='process_exposure'
    )
    qa_tests = JSONField(
        default={},
        help_text='QA tests summary.'
    )
    configuration = models.ForeignKey(
        Configuration,
        blank=True,
        null=True,
        related_name='process_configuration'
    )


class Camera(models.Model):
    """Camera information"""
    camera = models.CharField(
        max_length=2,
        help_text='Camera ID',
        primary_key=True
    )
    spectrograph = models.CharField(
        max_length=1,
        help_text='Spectrograph ID'
    )
    arm = models.CharField(
        max_length=1,
        help_text='Arm ID'
    )

    def __str__(self):
        return str(self.camera)


class Job(models.Model):
    """Job information"""

    STATUS_OK = 0
    STATUS_FAILED = 1
    STATUS_RUNNING = 2

    name = models.CharField(
        max_length=45,
        default='Quick Look',
        help_text='Name of the job.'
    )
    start = models.DateTimeField(
        auto_now=True,
        help_text='Datetime when the job was started'
    )
    end = models.DateTimeField(
        blank=True, null=True,
        help_text='Datetime when the job was finished.'
    )
    status = models.SmallIntegerField(
        default=STATUS_RUNNING,
        help_text='Job status, 0=OK, 1=Failed, 2=Running'
    )
    version = models.CharField(
        max_length=16, null=True,
        help_text='Version of the pipeline'
    )
    camera = models.ForeignKey(Camera, related_name='camera_jobs')
    process = models.ForeignKey(
        Process, related_name='process_jobs',
        on_delete=models.CASCADE
    )
    logname = models.CharField(
        max_length=65, null=True,
        help_text='Name of the log file.'
    )
    output = JSONField(
        help_text='JSON structure with the QA result',
        null=True
    )

    def __str__(self):
        return str(self.name)

class Product(models.Model):
    job = models.ForeignKey(Job, related_name='product_job')
    value = ArrayField(models.FloatField())
    key = models.CharField(
        max_length=30,
        help_text='Metric Key'
    )
    mjd = models.FloatField(
        help_text='MJD',
        null=True
    )

class Fibermap(models.Model):
    """Fibermap information"""
    fiber_ra = ArrayField(models.FloatField())
    fiber_dec = ArrayField(models.FloatField())
    fiber = ArrayField(models.FloatField())
    objtype = ArrayField(models.CharField(max_length=15))
    exposure = models.ForeignKey(Exposure, related_name='fibermap_exposure')


class ProcessComment(models.Model):
    """Process comment"""
    text = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, default=1)
    process = models.ForeignKey(Process, related_name='process_comments')
    date = models.DateField(default=date.today)

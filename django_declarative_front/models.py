"""
Django models for WebFunReflex framework.

These models can be used to store state machine configurations,
workflow definitions, and other framework-related data.
"""

from django.db import models


class StateMachineConfig(models.Model):
    """Configuration for state machines."""
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    config = models.JSONField(default=dict)
    
    class Meta:
        verbose_name = "State Machine Configuration"
        verbose_name_plural = "State Machine Configurations"
    
    def __str__(self):
        return self.name


class WorkflowDefinition(models.Model):
    """Definition for workflow processing."""
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    steps = models.JSONField(default=list)
    
    class Meta:
        verbose_name = "Workflow Definition"
        verbose_name_plural = "Workflow Definitions"
    
    def __str__(self):
        return self.name
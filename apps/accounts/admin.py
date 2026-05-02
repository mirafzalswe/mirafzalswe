from django.contrib import admin
from django.utils import timezone

from .models import AccessRequest, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "has_personal_access", "access_requested_at")
    list_filter = ("has_personal_access",)
    search_fields = ("user__username", "user__email")


@admin.register(AccessRequest)
class AccessRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "created_at", "decided_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email", "reason")
    readonly_fields = ("created_at", "decided_at")
    actions = ("approve_requests", "reject_requests")

    @admin.action(description="Approve selected requests")
    def approve_requests(self, request, queryset):
        for ar in queryset.filter(status=AccessRequest.Status.PENDING):
            ar.status = AccessRequest.Status.APPROVED
            ar.decided_at = timezone.now()
            ar.save()
            profile = ar.user.profile
            profile.has_personal_access = True
            profile.save(update_fields=["has_personal_access"])
        self.message_user(request, "Selected requests approved.")

    @admin.action(description="Reject selected requests")
    def reject_requests(self, request, queryset):
        for ar in queryset.filter(status=AccessRequest.Status.PENDING):
            ar.status = AccessRequest.Status.REJECTED
            ar.decided_at = timezone.now()
            ar.save()
        self.message_user(request, "Selected requests rejected.")

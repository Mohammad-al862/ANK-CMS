from django.contrib import admin
from .models import Project, Task, Manager, Supervisor, Worker,Resource


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'budget', 'timeline', 'supervisor')
    search_fields = ('name', 'location')
    list_filter = ('timeline', 'supervisor')

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'start_date', 'end_date')
    search_fields = ('title', 'project__name')
    list_filter = ('start_date', 'end_date')

class ManagerAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username', 'user__email')

class SupervisorAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username', 'user__email')

class WorkerAdmin(admin.ModelAdmin):
    list_display = ('name', 'adhar_no', 'is_working')
    search_fields = ('name', 'adhar_no')



class ResourceAdmin(admin.ModelAdmin):
    list_display = ('material_type', 'total_quantity', 'quantity_used', 'quantity_left', 'arrival_date', 'project')  # Fields to display in list view
    search_fields = ('material_type', 'project__name')  # Allow searching by material type and project name
    list_filter = ('material_type', 'project')  # Filter by material type and project
    ordering = ('material_type',)  # Default ordering by material type

    # Optional: Organize fields in the admin form using fieldsets
    fieldsets = (
        (None, {
            'fields': ('material_type', 'total_quantity', 'quantity_used', 'arrival_date', 'project')
        }),
    )

    # Make the `quantity_left` field read-only, as it is computed automatically
    readonly_fields = ('quantity_left',)

   
# Register models with the admin site
admin.site.register(Project, ProjectAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Manager, ManagerAdmin)
admin.site.register(Supervisor, SupervisorAdmin)
admin.site.register(Worker, WorkerAdmin)
admin.site.register(Resource, ResourceAdmin)

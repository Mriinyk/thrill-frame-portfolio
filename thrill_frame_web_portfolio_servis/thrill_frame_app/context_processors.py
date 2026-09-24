from thrill_frame_app.models import PhotoSession, SiteVisit, VideoWork


def footer_stats(request):
    visit = SiteVisit.objects.filter(id=1).first()

    return {
        "visits_count": visit.count if visit else 0,
        "videos_count": VideoWork.objects.count(),
        "photos_count": PhotoSession.objects.count(),
    }

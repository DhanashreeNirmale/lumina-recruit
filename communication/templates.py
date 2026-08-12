def shortlist_message(candidate_name, job_title):

    return f"""
Subject: Your Application Has Been Shortlisted

Dear {candidate_name},

We are pleased to inform you that your profile has been
shortlisted for the {job_title} position.

Our recruitment team will contact you with the next steps.

Regards,
Recruitment Team
""".strip()


def interview_message(
    candidate_name,
    job_title,
    interview_date,
    interview_time
):

    return f"""
Subject: Interview Invitation - {job_title}

Dear {candidate_name},

Your application for the {job_title} position has progressed
to the interview stage.

Interview Date: {interview_date}
Interview Time: {interview_time}

Please be available at the scheduled time.

Regards,
Recruitment Team
""".strip()


def assessment_message(
    candidate_name,
    job_title,
    assessment_url
):

    return f"""
Subject: Technical Assessment - {job_title}

Dear {candidate_name},

You have been invited to complete the technical assessment
for the {job_title} position.

Assessment Link:
{assessment_url}

Regards,
Recruitment Team
""".strip()
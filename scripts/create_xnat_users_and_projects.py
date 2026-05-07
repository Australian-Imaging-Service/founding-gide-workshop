import sys
import tempfile
import xnat
from pathlib import Path
from medimages4tests.mri.neuro.t1w import get_image as openneuro_t1w

password = sys.argv[1]

NUM_USERS = 15

SIMPLE_DIR_SUBJECTS = [("subject01", "subject01_1"), ("subject02", "subject02_1")]
OPENNEURO_SUBJECTS = [("subject01", "subject01_MR01"), ("subject02", "subject02_MR01")]

XNAT_HOST = "https://xnat.neurodesk.org/"


def create_project(session, project_id):
    session.put(f"/data/archive/projects/{project_id}")
    session.projects.clearcache()
    return session.projects[project_id]


def populate_simple_dir(session, xproject, a_dir):
    for subject_id, session_id in SIMPLE_DIR_SUBJECTS:
        xsubject = session.classes.SubjectData(label=subject_id, parent=xproject)
        xsession = session.classes.MrSessionData(label=session_id, parent=xsubject)
        xscan = session.classes.MrScanData(id=1, type="a-directory", parent=xsession)
        resource = xscan.create_resource("DIRECTORY")
        resource.upload_dir(a_dir.parent, method="tar_file")


def populate_openneuro_t1w(session, xproject, t1w_path):
    for subject_id, session_id in OPENNEURO_SUBJECTS:
        xsubject = session.classes.SubjectData(label=subject_id, parent=xproject)
        xsession = session.classes.MrSessionData(label=session_id, parent=xsubject)
        xscan = session.classes.MrScanData(id=1, type="t1w", parent=xsession)
        resource = xscan.create_resource("NIFTI")
        resource.upload_dir(t1w_path.parent, method="tar_file")


def grant_project_access(session, project_id, username):
    session.put(f"/data/projects/{project_id}/users/Members/{username}")


print("Preparing test data...")
t1w_path = openneuro_t1w()

tmp_dir = Path(tempfile.mkdtemp())
a_dir = tmp_dir / "a-dir"
a_dir.mkdir()
for k in range(3):
    (a_dir / f"file{k + 1}.txt").write_text(f"A dummy file - {k + 1}\n")

print("Creating XNAT users and projects...")
with xnat.connect(XNAT_HOST, user="admin", password=password) as session:
    for i in range(NUM_USERS + 1):
        username = f"user{i}"
        print(f"Creating {username}...")

        session.post(
            "/xapi/users",
            json={
                "username": username,
                "password": f"password{i}",
                "email": f"user{i}@workshop.example.com",
                "firstName": "User",
                "lastName": str(i),
                "enabled": True,
                "verified": True,
            },
        )

        simple_dir_id = f"SIMPLE_DIR_{i}"
        xproject = create_project(session, simple_dir_id)
        populate_simple_dir(session, xproject, a_dir)
        grant_project_access(session, simple_dir_id, username)

        openneuro_id = f"OPENNEURO_T1W_{i}"
        xproject = create_project(session, openneuro_id)
        populate_openneuro_t1w(session, xproject, t1w_path)
        grant_project_access(session, openneuro_id, username)

        print(f"  -> {simple_dir_id}, {openneuro_id}")

print("Done.")

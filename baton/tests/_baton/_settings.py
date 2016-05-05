from testwithbaton.irods import IrodsVersion
from testwithbaton.models import BatonImage


BATON_IMAGE = BatonImage(
    tag="wtsi-hgi/baton:specificquery",
    path="github.com/wtsi-hgi/docker-baton.git",
    docker_file="custom/irods-3.3.1/Dockerfile",
    build_args={
        "REPOSITORY": "https://github.com/wtsi-hgi/baton.git",
        "BRANCH": "feature/specificquery"
    }
)

IRODS_VERSION = IrodsVersion.v3_3_1

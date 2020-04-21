"""Add UploadedBlob table

Revision ID: 3383aad1e992
Revises: e8e27f36f87d
Create Date: 2020-04-21 11:45:54.837077

"""

# revision identifiers, used by Alembic.
revision = "3383aad1e992"
down_revision = "e8e27f36f87d"

import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade(op, tables, tester):
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "uploadedblob",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("repository_id", sa.Integer(), nullable=False),
        sa.Column("blob_id", sa.Integer(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["blob_id"], ["imagestorage.id"], name=op.f("fk_uploadedblob_blob_id_imagestorage")
        ),
        sa.ForeignKeyConstraint(
            ["repository_id"],
            ["repository.id"],
            name=op.f("fk_uploadedblob_repository_id_repository"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_uploadedblob")),
    )
    op.create_index("uploadedblob_blob_id", "uploadedblob", ["blob_id"], unique=False)
    op.create_index("uploadedblob_expires_at", "uploadedblob", ["expires_at"], unique=False)
    op.create_index("uploadedblob_repository_id", "uploadedblob", ["repository_id"], unique=False)
    # ### end Alembic commands ###

    # ### population of test data ### #
    tester.populate_table(
        "uploadedblob",
        [
            ("repository_id", tester.TestDataType.Foreign("repository")),
            ("blob_id", tester.TestDataType.Foreign("imagestorage")),
            ("uploaded_at", tester.TestDataType.DateTime),
            ("expires_at", tester.TestDataType.DateTime),
        ],
    )
    # ### end population of test data ### #


def downgrade(op, tables, tester):
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("uploadedblob")
    # ### end Alembic commands ###

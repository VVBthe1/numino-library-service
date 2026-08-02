import grpc
from google.protobuf import empty_pb2
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import NoResultFound

from app.database import session_scope
from app.pb import member_pb2, member_pb2_grpc
from app.repositories.loan import LoanRepository
from app.repositories.member import MemberRepository
from app.rpc.mappers.book import member_to_proto
from app.services.member import MemberService


def _member_service(db) -> MemberService:
    return MemberService(MemberRepository(db), LoanRepository(db))


class MemberServicer(member_pb2_grpc.MemberServiceServicer):
    def CreateMember(self, request, context):
        try:
            with session_scope() as db:
                service = _member_service(db)
                member = service.create(
                    name=request.name,
                    email=request.email,
                    phone=request.phone if request.HasField("phone") else None,
                    address=request.address if request.HasField("address") else None,
                    membership_start_date=request.membership_start_date,
                    membership_end_date=request.membership_end_date
                    if request.HasField("membership_end_date")
                    else None,
                )
                return member_pb2.CreateMemberResponse(member=member_to_proto(member))
        except ValueError as exc:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(exc))
            return member_pb2.CreateMemberResponse()

    def GetMember(self, request, context):
        try:
            with session_scope() as db:
                service = _member_service(db)
                member = service.get(request.id)
                return member_pb2.GetMemberResponse(member=member_to_proto(member))
        except ValueError as exc:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(exc))
            return member_pb2.GetMemberResponse()
        except NoResultFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"member {request.id} not found")
            return member_pb2.GetMemberResponse()

    def ListMembers(self, request, context):
        try:
            with session_scope() as db:
                service = _member_service(db)
                members = service.list(
                    name_query=request.name_query
                    if request.HasField("name_query")
                    else None,
                    email_query=request.email_query
                    if request.HasField("email_query")
                    else None,
                    limit=request.page_size or 50,
                )
                return member_pb2.ListMembersResponse(
                    members=[member_to_proto(member) for member in members],
                )
        except ValueError as exc:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(exc))
            return member_pb2.ListMembersResponse()

    def UpdateMember(self, request, context):
        try:
            with session_scope() as db:
                service = _member_service(db)
                member = service.update(
                    request.id,
                    name=request.name,
                    email=request.email,
                    phone=request.phone if request.HasField("phone") else None,
                    address=request.address if request.HasField("address") else None,
                    membership_start_date=request.membership_start_date,
                    membership_end_date=request.membership_end_date
                    if request.HasField("membership_end_date")
                    else None,
                )
                return member_pb2.UpdateMemberResponse(member=member_to_proto(member))
        except ValueError as exc:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(exc))
            return member_pb2.UpdateMemberResponse()
        except NoResultFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"member {request.id} not found")
            return member_pb2.UpdateMemberResponse()

    def DeleteMember(self, request, context):
        try:
            with session_scope() as db:
                service = _member_service(db)
                service.delete(request.id)
                return empty_pb2.Empty()
        except ValueError as exc:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(exc))
            return empty_pb2.Empty()
        except NoResultFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"member {request.id} not found")
            return empty_pb2.Empty()
        except IntegrityError:
            context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            context.set_details("cannot delete member referenced by loans")
            return empty_pb2.Empty()

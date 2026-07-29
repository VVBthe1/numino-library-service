import grpc
from google.protobuf import empty_pb2

from app.pb import member_pb2, member_pb2_grpc


class MemberServicer(member_pb2_grpc.MemberServiceServicer):
    def CreateMember(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("CreateMember not implemented")
        return member_pb2.CreateMemberResponse()

    def GetMember(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("GetMember not implemented")
        return member_pb2.GetMemberResponse()

    def ListMembers(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("ListMembers not implemented")
        return member_pb2.ListMembersResponse()

    def UpdateMember(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("UpdateMember not implemented")
        return member_pb2.UpdateMemberResponse()

    def DeleteMember(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("DeleteMember not implemented")
        return empty_pb2.Empty()

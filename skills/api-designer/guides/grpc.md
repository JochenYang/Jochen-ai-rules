# gRPC API Design Guide

Best practices for designing gRPC services.

## Protocol Buffers

### Service Definition
```protobuf
syntax = "proto3";

package user.v1;

option go_package = "example.com/api/user/v1";

// User service definition
service UserService {
  // Get a single user
  rpc GetUser(GetUserRequest) returns (GetUserResponse);

  // List users with pagination
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);

  // Create a new user
  rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);

  // Update an existing user
  rpc UpdateUser(UpdateUserRequest) returns (UpdateUserResponse);

  // Delete a user
  rpc DeleteUser(DeleteUserRequest) returns (DeleteUserResponse);
}

// Message definitions
message User {
  string id = 1;
  string email = 2;
  string name = 3;
  UserRole role = 4;
  string created_at = 5;
  string updated_at = 6;
}

enum UserRole {
  USER_ROLE_UNSPECIFIED = 0;
  USER_ROLE_USER = 1;
  USER_ROLE_ADMIN = 2;
}

message GetUserRequest {
  string id = 1;
}

message GetUserResponse {
  User user = 1;
}

message ListUsersRequest {
  int32 page_size = 1;
  string page_token = 2;
  string filter = 3;
}

message ListUsersResponse {
  repeated User users = 1;
  string next_page_token = 2;
  int32 total_size = 3;
}

message CreateUserRequest {
  string email = 1;
  string name = 2;
  string password = 3;
  UserRole role = 4;
}

message CreateUserResponse {
  User user = 1;
}

message UpdateUserRequest {
  string id = 1;
  User update_mask = 2;
  User user = 3;
}

message UpdateUserResponse {
  User user = 1;
}

message DeleteUserRequest {
  string id = 1;
}

message DeleteUserResponse {
  bool success = 1;
}
```

## Design Principles

### Message Design
- Use singular names for fields
- Use optional for nullable fields (proto3 syntax)
- Number fields sequentially from 1
- Reserve deleted field numbers/names

### Error Handling
```go
// Standard error codes
const (
  OK                 codes.Code = 0
  Cancelled          codes.Code = 1
  Unknown            codes.Code = 2
  InvalidArgument    codes.Code = 3
  NotFound           codes.Code = 4
  AlreadyExists      codes.Code = 5
  PermissionDenied   codes.Code = 6
  ResourceExhausted  codes.Code = 7
  FailedPrecondition codes.Code = 8
  Aborted            codes.Code = 9
  OutOfRange         codes.Code = 10
  Unimplemented      codes.Code = 12
  Internal           codes.Code = 13
  Unavailable        codes.Code = 14
  DataLoss           codes.Code = 15
  Unauthenticated    codes.Code = 16
)
```

### Streaming
```protobuf
// Server streaming
rpc ListUsers(ListUsersRequest) returns (stream User);

// Client streaming
rpc UploadUsers(stream UserUploadRequest) returns (UploadUsersResponse);

// Bidirectional streaming
rpc StreamMessages(stream MessageRequest) returns (stream MessageResponse);
```

## Best Practices

### Compatibility
- Never change field numbers
- Never change field types
- Add new fields as optional
- Use reserved fields for deleted numbers

### Performance
- Use proto3 for simplicity
- Enable compression (gzip, snappy)
- Use connection pooling
- Implement keepalive

### Documentation
- Use comments above field definitions
- Include usage examples
- Document deprecation

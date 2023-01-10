pub enum UserUCError {
    FatalError,
    TemporaryError,
    NotFoundError,
    AlreadyExists,
}

#[derive(Debug)]
pub enum SignError {
    FatalError,
    TemporaryError,
    VerificationError,
}

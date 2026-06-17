const KNOWN_ERROR_CODES = {
  invalid_credentials: "Invalid email or password",
  email_already_exists: "An account with this email already exists",
  unauthorized: "Unauthorized",
  missing_user_id: "Unauthorized",
  user_not_found: "User not found",
  category_not_found: "Category not found",
  tag_not_found: "Tag not found",
  expense_not_found: "Expense not found",
  export_not_found: "Export job not found",
  category_in_use: "Cannot delete category while expenses use it",
  category_duplicate_name: "A category with this name already exists",
  tag_duplicate_name: "A tag with this name already exists",
  missing_bearer_token: "Please sign in again",
  missing_refresh_token: "Please sign in again",
  invalid_token: "Session expired. Please sign in again",
  validation_error: "Validation failed",
  service_unavailable: "Service temporarily unavailable",
  invalid_upstream_response: "Unexpected server response",
};

export function getErrorMessage(error, fallback = "Something went wrong") {
  const detail = error?.data?.detail;
  const code = error?.data?.code;

  if (typeof detail === "string" && detail) {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg ?? String(item)).join(", ");
  }

  if (typeof code === "string" && KNOWN_ERROR_CODES[code]) {
    return KNOWN_ERROR_CODES[code];
  }

  if (error instanceof Error && error.message) {
    return error.message;
  }

  return fallback;
}

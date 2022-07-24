data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_role" {
  name               = "lambda-test-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json
}

# resource "aws_lambda_function" "test_lambda" {
#   # If the file is not in the current working directory you will need to include a 
#   # path.module in the filename.
#   filename      = "lambda.zip"
#   function_name = "Friction_Test"
#   role          = aws_iam_role.lambda_role.arn
#   handler       = "main.lambda_handler"

#   # The filebase64sha256() function is available in Terraform 0.11.12 and later
#   # For Terraform 0.11.11 and earlier, use the base64sha256() function and the file() function:
#   # source_code_hash = "${base64sha256(file("lambda_function_payload.zip"))}"
#   source_code_hash = filebase64sha256(data.archive_file.python_lambda_package.out)

#   runtime = "python3.6"

#   environment {
#     variables = {
#       foo = "bar"
#     }
#   }
# }

data "archive_file" "python_lambda_package" {  
  type = "zip"  
  source_file = "${path.module}/../src/main.py" 
  output_path = "lambda.zip"
}
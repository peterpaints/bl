from flask_restplus import reqparse

pagination_arguments = reqparse.RequestParser()
pagination_arguments.add_argument('page', type=int, required=False, default=1, help='Page number')
pagination_arguments.add_argument('per_page', type=int, required=False, choices=[2, 5, 10, 15, 20, 25, 100],
                                  default=5, help='Results per page {error_msg}')
pagination_arguments.add_argument('q', required=False, help='Search term')

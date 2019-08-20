from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)
        if email is None:
            RESPONSE_MSG = {
                'msg_code': 'MG000',
                'success': 0,
                'results': "[]",
                'errors': "[{'error_code':'', 'error_msg':'email address is required to log in.'}]"
            }
            raise serializers.ValidationError(RESPONSE_MSG)
        if password is None:
            RESPONSE_MSG = {
                'msg_code': 'MG000',
                'success': 0,
                'results': "[]",
                'errors': "[{'error_code':'', 'error_msg':'A password is required to log in.'}]"
            }
            raise serializers.ValidationError(RESPONSE_MSG)

        # print(user.is_authenticated)
        # if user is None:
        #     raise serializers.ValidationError(
        #         'A user with this email and password was not found.'
        #     )
        # if not user.is_active:
        #     raise serializers.ValidationError(
        #         'This user has been deactivated.'
        #     )
        # # user = authenticate(username=email, password=password)
        # # login(self.request, user)
        #
        # return {
        #     'password': user.password,
        #     'email': user.email,
        #     'username': user.username,
        #     #'token': user.token
        # }
        return {
            'email': email,
            'password': password,
        }
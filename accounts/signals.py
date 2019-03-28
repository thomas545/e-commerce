from django.dispatch import Signal

# craeting Signals , Defining and sending signals


user_login_signals = Signal(providing_args=['instance', 'request'])

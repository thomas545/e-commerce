from django.dispatch import Signal

# craeting Signals , Defining and sending signals



object_viewed_signal = Signal(providing_args=['instance', 'request'])

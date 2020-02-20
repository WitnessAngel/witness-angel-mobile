from waclient.common_config import PACKAGE_NAME

CHANNEL_ID = PACKAGE_NAME


def _set_icons(context, notification, icon=None):
    '''
    Set the small application icon displayed at the top panel together with
    WiFi, battery percentage and time and the big optional icon (preferably
    PNG format with transparent parts) displayed directly in the
    notification body.
    .. versionadded:: 1.4.0
    '''

    from jnius import autoclass
    BitmapFactory = autoclass('android.graphics.BitmapFactory')
    Drawable = autoclass("{}.R$drawable".format(PACKAGE_NAME))

    app_icon = Drawable.icon
    notification.setSmallIcon(app_icon)

    """
    if icon == '':
            # we don't want the big icon set,
            # only the small one in the top panel
            pass
    elif icon:
        bitmap_icon = BitmapFactory.decodeFile(icon)
        notification.setLargeIcon(bitmap_icon)
    else:
        bitmap_icon = BitmapFactory.decodeResource(
            python_act.getResources(), app_icon
        )
        notification.setLargeIcon(bitmap_icon)
    """


def _set_open_behavior(context, notification):
    '''
    Open the source application when user opens the notification.
    .. versionadded:: 1.4.0
    '''

    from jnius import autoclass
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    from android import python_act

    # create Intent that navigates back to the application
    app_context = context.getApplication().getApplicationContext()
    notification_intent = Intent(app_context, python_act)

    # set flags to run our application Activity
    notification_intent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP)
    notification_intent.setAction(Intent.ACTION_MAIN)
    notification_intent.addCategory(Intent.CATEGORY_LAUNCHER)

    # get our application Activity
    pending_intent = PendingIntent.getActivity(
        app_context, 0, notification_intent, 0
    )

    notification.setContentIntent(pending_intent)
    notification.setAutoCancel(False)


def build_notification_channel(context, name):
    from jnius import autoclass

    manager = autoclass('android.app.NotificationManager')  # -> "notification"
    channel = autoclass('android.app.NotificationChannel')

    app_channel = channel(
         CHANNEL_ID, name, manager.IMPORTANCE_DEFAULT
    )
    context.getSystemService("notification").createNotificationChannel(
        app_channel
    )
    return app_channel


def build_notification(context, title, message, ticker ):
    from jnius import autoclass

    AndroidString = autoclass('java.lang.String')

    NotificationBuilder = autoclass('android.app.Notification$Builder')

    notification = NotificationBuilder(context, CHANNEL_ID)

    # set basic properties for notification
    notification.setContentTitle(title)
    notification.setContentText(AndroidString(message))
    notification.setTicker(AndroidString(ticker))

    # set additional flags for notification
    _set_icons(context, notification, icon=None)
    _set_open_behavior(context, notification)

    notification = notification.build()
    return notification


def display_notification(context, notification):
    from jnius import autoclass

    Context = autoclass('android.content.Context')

    notification_service = context.getSystemService(Context.NOTIFICATION_SERVICE)
    notification_service.notify(0, notification)

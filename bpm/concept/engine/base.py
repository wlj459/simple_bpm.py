# Access Control Levels
ACL_DEFAULT = 0
ACL_PUBLIC = 1
ACL_PROTECTED = 2
ACL_PRIVATE = 3

# RELEASE STATES
STATE_DEVELOPMENT = 0
STATE_STABLE = 1
STATE_DEPRECATED = 2

# Task Categories
CAT_PROCESS = 0
CAT_COMPONENT = 1


class BaseTask(object):

    # Access Control Levels
    ACL_DEFAULT = ACL_DEFAULT
    ACL_PUBLIC = ACL_PUBLIC
    ACL_PROTECTED = ACL_PROTECTED
    ACL_PRIVATE = ACL_PRIVATE

    def __init__(self, namespace):
        self.namespace = namespace

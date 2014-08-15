# AUVSI SUAS Puppet Module: django
# ==============================================================================

# django module definition
class auvsi_suas::django {

    # Prerequisite modules
    require auvsi_suas::apache
    require auvsi_suas::matplotlib
    require auvsi_suas::mysql
    require auvsi_suas::numpy
    require auvsi_suas::openssh
    require auvsi_suas::openssl
    require auvsi_suas::python
    require auvsi_suas::sqlite

    # Package list
    $package_deps = ["python-django",
                     "python-django-doc",
                     "python-django-horizon",
                     "python-django-maas",
                     "python-django-nose",
                     "python-django-openstack",
                     "python-django-piston",
                     "python-django-south",
                     "python-django-adminaudit",
                     "python-django-app-plugins",
                     "python-django-auth-ldap",
                     "python-django-auth-ldap-doc",
                     "python-django-auth-openid",
                     "python-django-authority",
                     "python-django-bitfield",
                     "python-django-braces",
                     "python-django-celery",
                     "python-django-celery-doc",
                     "python-django-classy-tags",
                     "python-django-configglue",
                     "python-django-conneg",
                     "python-django-contact-form",
                     "python-django-countries",
                     "python-django-crispy-forms",
                     "python-django-dajax",
                     "python-django-dajaxice",
                     "python-django-debug-toolbar",
                     "python-django-discover-runner",
                     "python-django-djapian",
                     "python-django-evolution",
                     "python-django-extdirect",
                     "python-django-extensions",
                     "python-django-extra-views",
                     "python-django-feincms",
                     "python-django-feincms-doc",
                     "python-django-filter",
                     "python-django-filters",
                     "python-django-filters-doc",
                     "python-django-floppyforms",
                     "python-django-formfieldset",
                     "python-django-genshi",
                     "python-django-guardian",
                     "python-django-guardian-doc",
                     "python-django-jsonfield",
                     "python-django-ldapdb",
                     "python-django-lint",
                     "python-django-localeurl",
                     "python-django-macaddress",
                     "python-django-mailer",
                     "python-django-markupfield",
                     "python-django-model-utils",
                     "python-django-mptt",
                     "python-django-mumble",
                     "python-django-notification",
                     "python-django-nova",
                     "python-django-oauth-plus",
                     "python-django-openid-auth",
                     "python-django-pagination",
                     "python-django-picklefield",
                     "python-django-pipeline",
                     "python-django-pipeline-doc",
                     "python-django-ratelimit",
                     "python-django-ratelimit-doc",
                     "python-django-registration",
                     "python-django-reversion",
                     "python-django-reversion-doc",
                     "python-django-rosetta",
                     "python-django-sekizai",
                     "python-django-shorturls",
                     "python-django-shortuuidfield",
                     "python-django-social-auth",
                     "python-django-tables2",
                     "python-django-tables2-doc",
                     "python-django-tagging",
                     "python-django-taggit",
                     "python-django-threaded-multihost",
                     "python-django-threadedcomments",
                     "python-django-tinymce",
                     "python-django-treebeard",
                     "python-django-treebeard-doc",
                     "python-django-voting",
                     "python-django-websocket"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}

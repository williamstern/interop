# AUVSI SUAS Puppet Module: server_setup
# Prepares server for running
# ==============================================================================

class auvsi_suas::server_setup {
    # First install the server
    require auvsi_suas::server_install
    # ... and the database
    require auvsi_suas::postgresql_setup

    # Prepare database
    exec { 'migrate auth':
        command => "python manage.py migrate auth",
        cwd => "/auvsi_suas_competition/src/auvsi_suas_server/",
    } ->
    exec { 'migrate sessions':
        command => "python manage.py migrate sessions",
        cwd => "/auvsi_suas_competition/src/auvsi_suas_server/",
    } ->
    exec { 'migrate admin':
        command => "python manage.py migrate admin",
        cwd => "/auvsi_suas_competition/src/auvsi_suas_server/",
    } ->
    exec { 'migrate':
        command => "python manage.py migrate --noinput",
        cwd => "/auvsi_suas_competition/src/auvsi_suas_server/",
    }

    # Copy all static files
    exec { 'collectstatic':
        command => "python manage.py collectstatic --noinput",
        cwd => "/auvsi_suas_competition/src/auvsi_suas_server/",
    }

    # Load initial testadmin superuser
    exec { 'testadmin superuser':
        command => "python manage.py loaddata fixtures/testadmin_superuser.yaml",
        cwd => "/auvsi_suas_competition/src/auvsi_suas_server/",
    }
}

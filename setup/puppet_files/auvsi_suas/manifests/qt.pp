# AUVSI SUAS Puppet Module: qt
# ==============================================================================

# qt module definition
class auvsi_suas::qt {

    # Prerequisite modules
    require auvsi_suas::gcc
    require auvsi_suas::jpeg-turbo
    require auvsi_suas::mysql
    require auvsi_suas::python
    require auvsi_suas::sqlite

    # Package list
    $package_deps = ["qt5-qmake",
                     "qt5-default",
                     "pyqt5-dev",
                     "libqt5concurrent5",
                     "libqt5core5a",
                     "libqt5designer5",
                     "libqt5designercomponents5",
                     "libqt5feedback5",
                     "libqt5gui5",
                     "libqt5help5",
                     "libqt5location5",
                     "libqt5location5-plugins",
                     "libqt5multimedia5",
                     "libqt5multimedia5-plugins",
                     "libqt5multimediawidgets5",
                     "libqt5network5",
                     "libqt5opengl5",
                     "libqt5opengl5-dev",
                     "libqt5positioning5",
                     "libqt5positioning5-plugins",
                     "libqt5printsupport5",
                     "libqt5sensors5",
                     "libqt5sensors5-dev",
                     "libqt5serialport5",
                     "libqt5serialport5-dev",
                     "libqt5sql5",
                     "libqt5sql5-sqlite",
                     "libqt5svg5",
                     "libqt5svg5-dev",
                     "libqt5test5",
                     "libqt5webkit5",
                     "libqt5webkit5-dev",
                     "libqt5widgets5",
                     "libqt5xml5",
                     "libqt5xmlpatterns5",
                     "libqt5xmlpatterns5-dev",
                     "libqt5multimedia5-touch",
                     "libqt5multimedia5-touch-plugins",
                     "libqt5multimediaquick-p5-touch",
                     "libqt5nfc5",
                     "libqt5publishsubscribe5",
                     "libqt5sql5-mysql",
                     "libqt5sql5-odbc",
                     "libqt5sql5-psql",
                     "libqt5sql5-tds",
                     "libqt5systeminfo5"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}

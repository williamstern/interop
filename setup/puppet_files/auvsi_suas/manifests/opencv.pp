# AUVSI SUAS Puppet Module: opencv
# ==============================================================================

# opencv module definition
class auvsi_suas::opencv {

    # Package list
    $package_deps = ["libopencv-calib3d-dev",
                     "libopencv-contrib-dev",
                     "libopencv-core-dev",
                     "libopencv-dev",
                     "libopencv-features2d-dev",
                     "libopencv-flann-dev",
                     "libopencv-highgui-dev",
                     "libopencv-imgproc-dev",
                     "libopencv-legacy-dev",
                     "libopencv-ml-dev",
                     "libopencv-objdetect-dev",
                     "libopencv-ocl-dev",
                     "libopencv-photo-dev",
                     "libopencv-stitching-dev",
                     "libopencv-superres-dev",
                     "libopencv-ts-dev",
                     "libopencv-video-dev",
                     "libopencv-videostab-dev"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}

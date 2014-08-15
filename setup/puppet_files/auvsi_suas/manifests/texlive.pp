# AUVSI SUAS Puppet Module: texlive
# ==============================================================================

# texlive module definition
class auvsi_suas::texlive {

    # Package list
    $package_deps = ["texlive",
                     "texlive-base",
                     "texlive-bibtex-extra",
                     "texlive-font-utils",
                     "texlive-fonts-extra-doc",
                     "texlive-fonts-recommended",
                     "texlive-generic-recommended",
                     "texlive-latex-base",
                     "texlive-latex-extra",
                     "texlive-latex-recommended",
                     "texlive-luatex",
                     "texlive-math-extra",
                     "texlive-pictures",
                     "texlive-pstricks",
                     "texlive-doc-en",
                     "texlive-fonts-extra",
                     "texlive-formats-extra",
                     "texlive-lang-english",
                     "texlive-latex3",
                     "texlive-metapost",
                     "texlive-music",
                     "texlive-omega",
                     "texlive-plain-extra",
                     "texlive-publishers",
                     "texlive-science"]

    # Install packages
    package { $package_deps:
        ensure => "latest",
    }
}



.. Nonlinear Signal Processing (nlsp) documentation master file, created by sphinx-quickstart on Mon Sep 05 09:40:53 2016.
.. You can adapt this file completely to your liking, but it should at least contain the root `toctree` directive.

Welcome to Nonlinear Signal Processing (nlsp)'s documentation!
==============================================================
.. some introduction to the library.

About:
   The Nonlinear Signal Processing (nlsp) is a python library which is written with the prime motive of modeling a nonlinear system.
   It provides classes to generate a nonlinear system, identifying a nonlinear system, and analyzing a nonlinear model.

   This nlsp library is the summary of the programs which I have written during my master thesis at HEAD acoustics GmbH.

Master Thesis:
   The final report of my thesis work can be found here :download:`Logesh_Masterthesis.pdf`. This report can be used to
   get the background information to use this library.

External Libraries:
   nlsp library depends on many standard python distributions which comes with the python package and also with some other
   packages which are listed below.

   SuMPF:
      The nlsp library uses SuMPF package written by Jonas Schulte-Coerne, who is also supervisor for my thesis, to do all the
      signal processing operations. The documentation of this package can be found here `SuMPF <http://jonassc.github.io/SuMPF/documentation/index.htm>`_.
      Thanks to Jonas for his well documented and helpful library.

   Numpy:
      The nlsp library uses Numpy library to do numerical operations using an array.

   matplotlib:
      The nlsp library used matplotlib library to plot the audio signals and spectrums.

Documentation:

   .. inheritance-diagram:: nlsp.model_generator nlsp.model_generator.modify_model nlsp.model_generator.change_nonlinearfunction
        :parts: 10

.. toctree::
        :maxdepth: 3

        nlsp

.. autosummary::
        :toctree: generated

        nlsp.aliasing_compensation



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


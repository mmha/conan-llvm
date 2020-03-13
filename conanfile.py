from conans import ConanFile, python_requires, tools
import os

base = python_requires("llvm-project/0.1@mmha/testing")

class IntelLLVMConan(base.llvm_base_project()):
    name = "llvm"
    version = "10.0.0-20190903"
    description = "LLVM Compiler Infrastructure"
    url = "https://llvm.org"
    license = "Apache-2.0"
    author = "LLVM"
    topics = ("llvm", "clang", "compiler")

    scm = {
        "type": "git",
        "url": "https://github.com/llvm/llvm-project.git",
        "revision": "ea366122d28f7756008543e495f1899b64f4060a",
    }

    @property
    def source_subfolder(self):
        return "llvm"

    llvm_cmake_options = {
        # Build targets
        "build_benchmarks": [True, False],
        "build_examples": [True, False],
        "build_instrumented_coverage": [True, False],
        "build_llvm_dylib": [True, False],
        "build_tests": [True, False],
        "build_tools": [True, False],
        "create_xcode_toolchain": [True, False],
        "install_binutils_symlinks": [True, False],
        "install_cctools_symlinks": [True, False],

        # Documentation
        "doxygen_svg": [True, False],
        "doxygen_qhp_namespace": "ANY",
        "enable_doxygen": [True, False],
        "enable_doxygen_qt_help": [True, False],
        "enable_sphinx": [True, False],

        # Debug options
        "abi_breaking_checks": ["WITH_ASSERTS", "FORCE_ON", "FORCE_OFF"],
        "enable_assertions": [True, False],
        "enable_expensive_checks": [True, False],
        "optimized_tablegen": [True, False],

        # C++ Feature support
        "enable_eh": [True, False],
        "enable_rtti": [True, False],
        "enable_threads": [True, False],
        "enable_unwind_tables": [True, False],

        # Profiling
        "profdata_file": "ANY",
        "use_oprofile": [True, False],
        "use_perf": [True, False],

        # Optional features
        "enable_bindings": [True, False],
        "enable_dia_sdk": [True, False],
        "enable_libedit": [True, False],
        "enable_ffi": [True, False],
        "enable_libpfm": [True, False],
        "enable_z3_solver": [True, False],
        "enable_zlib": [True, False],
        "use_intel_jitevents": [True, False],

        "append_vc_rev": [True, False],
        "link_llvm_dylib": [True, False],
        "target_arch": "ANY",
        "targets_to_build": "ANY",
        "use_newpm": [True, False],
    }

    default_llvm_cmake_options = {
        # Build targets
        "build_benchmarks": False,
        "build_examples": False,
        "build_instrumented_coverage": False,
        "build_llvm_dylib": False,
        "build_tests": False,
        "build_tools": True,
        "create_xcode_toolchain": True,
        "install_binutils_symlinks": False,
        "install_cctools_symlinks": False,

        # Documentation
        "doxygen_svg": False,
        "doxygen_qhp_namespace": "",
        "enable_doxygen": False,
        "enable_doxygen_qt_help": False,
        "enable_sphinx": False,

        # Debug options
        "abi_breaking_checks": "WITH_ASSERTS",
        "enable_assertions": False,
        "enable_expensive_checks": False,
        "optimized_tablegen": True,

        # C++ Feature support
        "enable_eh": False,
        "enable_rtti": False,
        "enable_threads": True,
        "enable_unwind_tables": True,

        # Profiling
        "profdata_file": "",
        "use_oprofile": False,
        "use_perf": False,

        # Optional features
        "enable_bindings": False,
        "enable_dia_sdk": False,
        "enable_libedit": False,
        "enable_ffi": False,
        "enable_libpfm": False,
        "enable_z3_solver": False,
        "enable_zlib": False,
        "use_intel_jitevents": False,

        "append_vc_rev": False,
        "link_llvm_dylib": False,
        "target_arch": "",
        "targets_to_build": "",
        "use_newpm": False,
    }

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        **llvm_cmake_options
    }
    default_options = {
        "shared": False,
        "fPIC": False,
        **default_llvm_cmake_options
    }

    @property
    def custom_cmake_definitions(self):
        return {
            "LLVM_BUILD_DOCS": True, # Already guarded by the doxygen/sphinx options
            "LLVM_INCLUDE_BENCHMARKS": self.options.build_benchmarks,
            "LLVM_INCLUDE_EXAMPLES": self.options.build_examples,
            "LLVM_INCLUDE_TESTS": self.options.build_tests,
            "LLVM_INCLUDE_TOOLS": self.options.build_tools,
        }

    def config_options(self):
        super().config_options()
        if not self.settings.os == "Macos":
            del self.options.create_xcode_toolchain
        if not self.settings.os == "Windows":
            del self.options.enable_dia_sdk
        if not "x86" in self.settings.arch:
            del self.options.use_intel_jitevents

    def configuration(self):
        if not self.options.enable_doxygen:
            for docopt in [self.options.doxygen_svg, self.options.enable_doxygen_qt_help]:
                if docopt:
                    raise errors.ConanInvalidConfiguration(f"{docopt} requires enable_doxygen to be set to True")
            if self.options.doxygen_qhp_namespace != "" and self.options.enable_doxygen_qt_help:
                    raise errors.ConanInvalidConfiguration("doxygen_qhp_namespace requires enable_doxygen_qt_help to be set to True")
        if self.options.enable_sphinx and tools.which("sphinx-build") is None:
            raise errors.ConanInvalidConfiguration("enable_sphinx is True but sphinx could not be found in PATH. Please install sphinx first.")

    def requirements(self):
        self.requires("netbsd-curses/0.3.1")
        self.requires("libxml2/2.9.9")

        if self.options.enable_doxygen:
            self.requires("doxygen_installer/1.8.15@bincrafters/stable")
        if self.options.enable_doxygen_qt_help:
            raise errors.ConanInvalidConfiguration("TODO: Qt")
        if self.options.enable_ffi:
            self.requires("libffi/3.3")
        if self.options.enable_libedit:
            self.requires("libedit/20190324-3.1@mmha/stable")
        if self.options.enable_libpfm:
            raise errors.ConanInvalidConfiguration("TODO libpfm")
        if self.options.enable_z3_solver:
            raise errors.ConanInvalidConfiguration("TODO: z3")
        if self.options.enable_zlib:
            self.requires("zlib/1.2.11")

    def system_requirements(self):
        if self.options.enable_sphinx and not tools.which("sphinx-build"):
            if os_info.linux_distro in ["ubuntu", "debian", "neon", "mint", "centos", "rhel", "fedora", "arch", "manjaro"]:
                SystemPackageTool().install(["python3-sphinx", "python-sphinx"])
            elif os_info.linux_distro in ["alpine"]:
                SystemPackageTool().install(["sphinx-python"])
            elif os_info.linux_distro in ["clear"]:
                SystemPackageTool().install(["python-extras"])
            else:
                raise errors.ConanInvalidConfiguration("enable_sphinx is True but sphinx could not be found. Please install sphinx first.")

    def package_info(self):
        super().package_info()

        if self.options.build_llvm_dylib:
            self.cpp_info.libs = ["LLVM"]
        else:
            self.cpp_info.libs = tools.collect_libs(self)

    def package_id(self):
        del self.info.options.build_benchmarks
        del self.info.options.build_examples
        del self.info.options.build_tests
        del self.info.options.optimized_tablegen
        del self.info.options.profdata_file

Name:           voicerecorder
Version:        0.6.0
Release:        1%{?dist}
Summary:        VoiceRecorder is a simple voice/audio recording application

License:        MIT
URL:            https://github.com/espdev/VoiceRecorder
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-pip
BuildRequires:  python3-packaging
BuildRequires:  python3-hatchling
BuildRequires:  pyproject-rpm-macros

Requires:       python3-pyside6

%description
VoiceRecorder is a simple voice/audio recording application.

%prep
%autosetup -n %{name}-%{version}

%generate_buildrequires
%pyproject_buildrequires -R

%build
%pyproject_wheel

%install
%pyproject_install

install -Dpm 644 voicerecorder.desktop %{buildroot}%{_datadir}/applications/voicerecorder.desktop
install -Dpm 644 icons/mic.png %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/voicerecorder.png

%files
%license LICENSE
%doc README.md
%{python3_sitelib}/voicerecorder*
%{_bindir}/voicerecorder
%{_datadir}/applications/voicerecorder.desktop
%{_datadir}/icons/hicolor/32x32/apps/voicerecorder.png

%changelog
* Tue Nov 04 2025 Evgeny Prilepin <esp.home@gmail.com> - 0.6.0
- Initial RPM release

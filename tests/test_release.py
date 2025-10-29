"""
Tests for release workflow and GitHub integration.

Run with: pytest tests/test_release.py -v
"""

import re
import yaml
from pathlib import Path


class TestReleaseWorkflow:
    """Test GitHub Actions release workflow configuration."""

    def test_release_workflow_exists(self):
        """Release workflow file should exist."""
        workflow_file = Path(__file__).parent.parent / ".github" / "workflows" / "release.yml"
        assert workflow_file.exists(), "release.yml workflow not found"

    def test_release_workflow_valid_yaml(self):
        """Release workflow should be valid YAML."""
        workflow_file = Path(__file__).parent.parent / ".github" / "workflows" / "release.yml"
        
        with open(workflow_file, 'r') as f:
            content = yaml.safe_load(f)
        
        assert content is not None
        assert 'name' in content
        # 'on' is a reserved word in YAML and gets parsed as True
        assert True in content or 'on' in content
        assert 'jobs' in content

    def test_release_workflow_triggers_on_tags(self):
        """Release workflow should trigger on version tags."""
        workflow_file = Path(__file__).parent.parent / ".github" / "workflows" / "release.yml"
        
        with open(workflow_file, 'r') as f:
            content = yaml.safe_load(f)
        
        # 'on' is a reserved word in YAML and gets parsed as True
        trigger_config = content.get(True) or content.get('on')
        assert trigger_config is not None
        assert 'push' in trigger_config
        assert 'tags' in trigger_config['push']
        
        # Should trigger on v*.*.* tags
        tags = trigger_config['push']['tags']
        assert 'v*.*.*' in tags

    def test_release_workflow_has_required_jobs(self):
        """Release workflow should have build and release jobs."""
        workflow_file = Path(__file__).parent.parent / ".github" / "workflows" / "release.yml"
        
        with open(workflow_file, 'r') as f:
            content = yaml.safe_load(f)
        
        jobs = content['jobs']
        assert 'build' in jobs, "Missing 'build' job"
        assert 'release' in jobs, "Missing 'release' job"

    def test_release_workflow_uses_build_reusable(self):
        """Release workflow should use the reusable build workflow."""
        workflow_file = Path(__file__).parent.parent / ".github" / "workflows" / "release.yml"
        
        with open(workflow_file, 'r') as f:
            content = yaml.safe_load(f)
        
        build_job = content['jobs']['build']
        assert 'uses' in build_job
        assert 'build-reusable.yml' in build_job['uses']

    def test_release_workflow_downloads_artifacts(self):
        """Release workflow should download artifacts for all platforms."""
        workflow_file = Path(__file__).parent.parent / ".github" / "workflows" / "release.yml"
        
        with open(workflow_file, 'r') as f:
            content = yaml.safe_load(f)
        
        release_job = content['jobs']['release']
        steps = release_job['steps']
        
        # Find download artifact steps
        download_steps = [s for s in steps if s.get('uses', '').startswith('actions/download-artifact')]
        
        # Should download for all 3 platforms
        assert len(download_steps) == 3, "Should download artifacts for Windows, macOS, and Linux"
        
        # Check artifact names
        artifact_names = [s['with']['name'] for s in download_steps]
        assert 'Mouser_windows-latest' in artifact_names
        assert 'Mouser_macos-latest' in artifact_names
        assert 'Mouser_ubuntu-latest' in artifact_names

    def test_release_workflow_uploads_all_platforms(self):
        """Release workflow should upload zip files for all platforms."""
        workflow_file = Path(__file__).parent.parent / ".github" / "workflows" / "release.yml"
        
        with open(workflow_file, 'r') as f:
            content = yaml.safe_load(f)
        
        release_job = content['jobs']['release']
        steps = release_job['steps']
        
        # Find the create release step
        create_release_step = None
        for step in steps:
            if 'softprops/action-gh-release' in step.get('uses', ''):
                create_release_step = step
                break
        
        assert create_release_step is not None, "Create release step not found"
        
        # Check that files are uploaded
        files = create_release_step['with']['files']
        assert 'Mouser_windows.zip' in files
        assert 'Mouser_macos.zip' in files
        assert 'Mouser_linux.zip' in files


class TestBuildWorkflow:
    """Test multi-platform build workflow configuration."""

    def test_build_workflow_exists(self):
        """Build workflow file should exist."""
        workflow_file = Path(__file__).parent.parent / ".github" / "workflows" / "build-reusable.yml"
        assert workflow_file.exists(), "build-reusable.yml workflow not found"

    def test_build_workflow_matrix_includes_all_platforms(self):
        """Build workflow should include Windows, macOS, and Linux in matrix."""
        workflow_file = Path(__file__).parent.parent / ".github" / "workflows" / "build-reusable.yml"
        
        with open(workflow_file, 'r') as f:
            content = yaml.safe_load(f)
        
        matrix = content['jobs']['build']['strategy']['matrix']
        os_list = matrix['os']
        
        assert 'windows-latest' in os_list
        assert 'macos-latest' in os_list
        assert 'ubuntu-latest' in os_list

    def test_build_workflow_includes_version_file(self):
        """Build workflow should include version.py in PyInstaller bundle."""
        workflow_file = Path(__file__).parent.parent / ".github" / "workflows" / "build-reusable.yml"
        
        with open(workflow_file, 'r') as f:
            content = f.read()
        
        # Check for version.py in PyInstaller command
        assert 'version.py' in content, "version.py should be included in PyInstaller bundle"


class TestReleaseHelper:
    """Test release helper script."""

    def test_release_script_exists(self):
        """Release helper script should exist."""
        script_file = Path(__file__).parent.parent / "scripts" / "create_release.py"
        assert script_file.exists(), "create_release.py script not found"

    def test_release_script_is_executable(self):
        """Release script should be a valid Python file."""
        script_file = Path(__file__).parent.parent / "scripts" / "create_release.py"
        
        # Should be able to read and parse the file (use utf-8 encoding)
        content = script_file.read_text(encoding='utf-8')
        assert '#!/usr/bin/env python' in content or 'import' in content

    def test_release_script_has_version_validation(self):
        """Release script should validate version format."""
        script_file = Path(__file__).parent.parent / "scripts" / "create_release.py"
        content = script_file.read_text(encoding='utf-8')
        
        # Should have version validation logic
        assert 'validate_version' in content
        assert r'\d+\.\d+\.\d+' in content  # Regex for X.Y.Z format


class TestVersionTag:
    """Test version tag format expectations."""

    def test_version_tag_pattern(self):
        """Test that version tag pattern matches expected format."""
        pattern = r'^v\d+\.\d+\.\d+$'
        
        # Valid tags
        assert re.match(pattern, 'v1.0.0')
        assert re.match(pattern, 'v1.2.3')
        assert re.match(pattern, 'v10.5.2')
        
        # Invalid tags
        assert not re.match(pattern, '1.0.0')  # Missing 'v'
        assert not re.match(pattern, 'v1.0')  # Missing patch
        assert not re.match(pattern, 'v1.0.0-beta')  # Extra suffix

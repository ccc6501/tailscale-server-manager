# Changelog

All notable changes to the Tailscale Server Manager are documented in this file.

## [2.0.0] - Enhanced Edition - 2024-11-21

### 🎉 Major Features Added

#### Settings Management System
- **NEW**: Comprehensive settings menu accessible from header
- **NEW**: Storage path configuration (logs, data, backups)
- **NEW**: Network configuration (Tailscale domain, API URL)
- **NEW**: Performance tuning (update intervals, stats retention)
- **NEW**: Safety features (port conflict checking, auto-restart option)
- **NEW**: Settings persistence in `settings.json` file
- **NEW**: Real-time settings updates via WebSocket broadcast

#### Service Management Enhancements
- **NEW**: Add Service wizard with GUI form
- **NEW**: Service validation before adding
  - Name uniqueness checking
  - Port conflict detection
  - Required field validation
- **NEW**: Service deletion endpoint
- **NEW**: Per-service configuration expanded:
  - Port list support
  - API URL field
  - Tailscale URL field
  - Description field
- **NEW**: Port scanning for running services
- **NEW**: Automatic port conflict detection

#### Monitoring & Tracking
- **NEW**: System statistics dashboard
  - Real-time CPU usage
  - Memory usage (percentage and GB)
  - Disk usage (percentage and GB)
- **NEW**: Service uptime tracking
  - Start time recording
  - Live uptime calculation
  - Human-readable format (days, hours, minutes)
- **NEW**: Error tracking system
  - Per-service error history (last 10)
  - Last error display on cards
  - Error timestamps
  - Visual error indicators (red border)
- **NEW**: Restart counter per service
- **NEW**: Process details enhancement
  - CPU percentage per process
  - Memory usage per process
  - Process creation time

#### Port Management
- **NEW**: Port conflict detection API
- **NEW**: Port status indicators on service cards
  - Active ports (green badge)
  - Inactive ports (gray badge)
- **NEW**: Port scanning functionality
- **NEW**: Port accessibility checking
- **NEW**: System-wide port usage detection
- **NEW**: Validation prevents port conflicts

#### User Interface Enhancements
- **NEW**: Enhanced service cards with:
  - Uptime display
  - Port status badges
  - API/Tailscale URLs (clickable)
  - Error messages inline
  - Restart count
  - Service description
  - Comprehensive process info
- **NEW**: System stats cards in header
- **NEW**: Modal dialogs for:
  - Settings configuration
  - Add service wizard
- **NEW**: Port conflict checker button
- **NEW**: Delete service option (API only, UI pending)
- **IMPROVED**: Card layout with more information density
- **IMPROVED**: Visual hierarchy and readability
- **IMPROVED**: Toast notifications for all actions
- **IMPROVED**: Error state visualization

#### Backend Architecture
- **NEW**: Pydantic models for API validation
- **NEW**: Settings persistence layer
- **NEW**: ServiceRuntime class for tracking
- **NEW**: Port management utilities
- **NEW**: Service validation system
- **NEW**: Enhanced error handling
- **NEW**: System statistics collection
- **NEW**: Port scanning functionality
- **NEW**: Conflict detection algorithms

#### API Endpoints
- **NEW**: `GET /api/settings` - Retrieve settings
- **NEW**: `POST /api/settings` - Update settings
- **NEW**: `GET /api/stats` - Get system statistics
- **NEW**: `GET /api/port-conflicts` - Check conflicts
- **NEW**: `POST /api/service/add` - Add new service
- **NEW**: `DELETE /api/service/{name}` - Remove service
- **NEW**: `POST /api/service/{name}/scan-ports` - Scan ports

#### Documentation
- **NEW**: FEATURES.md - Comprehensive feature documentation
- **NEW**: START_HERE.md - Enhanced getting started guide
- **NEW**: CHANGELOG.md - This file
- **UPDATED**: README.md - Complete rewrite with new features
- **UPDATED**: ARCHITECTURE.md - Updated system design

### 🔧 Improvements

#### Performance
- Optimized process scanning
- Reduced unnecessary API calls
- Efficient WebSocket updates
- Cached system statistics

#### Reliability
- Better error handling
- Graceful degradation
- Validation at multiple layers
- Safe defaults for all settings

#### User Experience
- Clearer visual feedback
- Comprehensive tooltips
- Inline help text
- Better error messages
- Confirmation prompts for dangerous actions

#### Code Quality
- Type hints throughout
- Dataclass models
- Separation of concerns
- Comprehensive comments
- Modular structure

### 🐛 Bug Fixes
- Fixed process detection race conditions
- Improved keyword matching accuracy
- Better handling of missing processes
- Fixed WebSocket disconnection handling
- Resolved port detection edge cases

### 🔒 Security
- Settings validation
- Input sanitization
- Safe file operations
- No external dependencies added
- Maintained local-only architecture

### ⚙️ Configuration
- **NEW**: settings.json format
- **CHANGED**: services_config.json - Added new optional fields
- **MAINTAINED**: Backward compatibility with old format

### 📋 Breaking Changes
- None! Fully backward compatible with v1.0 configurations

### 🎨 Visual Changes
- Enhanced service cards with more information
- System stats dashboard added
- Settings modal interface
- Add service wizard
- Port status badges
- Error message displays
- Improved color scheme consistency
- Better responsive behavior

---

## [1.0.0] - Initial Release - 2024-11-20

### Initial Features
- Basic service management (start/stop/restart)
- WebSocket real-time updates
- Service status monitoring
- Bulk operations
- Dark themed UI
- Tailscale remote access support
- Toast notifications
- Auto-reconnect capability
- Simple service configuration
- Process matching via keywords

---

## Upgrade Path

### From v1.0 to v2.0

1. **Backup your configuration**:
   ```bash
   cp services_config.json services_config.backup.json
   ```

2. **Update files**:
   - Replace `server.py`
   - Replace `index.html`
   - Add `settings.json` (will be created automatically)

3. **Update service configs** (optional):
   Add new fields to your services:
   ```json
   {
     "ports": [8000],
     "api_url": "http://localhost:8000",
     "tailscale_url": "https://service.ts.net",
     "description": "Service description"
   }
   ```

4. **Restart server**:
   ```bash
   python server.py
   ```

5. **Configure settings**:
   - Click Settings button
   - Configure your preferences
   - Save

That's it! Your services will continue to work as before, with all new features available.

---

## Future Roadmap

### Planned for v2.1
- [ ] Scheduled tasks (cron-like)
- [ ] Service dependencies
- [ ] Health check endpoints
- [ ] Email notifications
- [ ] Log viewer integration

### Planned for v2.2
- [ ] Multi-server support
- [ ] Service templates
- [ ] Resource usage graphs
- [ ] Historical data charts
- [ ] Advanced filtering

### Planned for v3.0
- [ ] Authentication system
- [ ] User roles and permissions
- [ ] API rate limiting
- [ ] Slack/Discord integration
- [ ] Mobile app (PWA)

---

## Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **Major**: Breaking changes
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes, backward compatible

---

**Current Version**: 2.0.0 (Enhanced Edition)

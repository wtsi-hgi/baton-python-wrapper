# Change Log
## 1.0.1 - 2016/10/21
### Changed
- Replicas and access controls are now optional properties in entities' JSON representation.
- Ensured decode and encode work with lists of `DataObject` and `Collection`.
- Improved and corrected issues in metadata mappers ([#41](https://github.com/wtsi-hgi/python-baton-wrapper/issues/41), [#44](https://github.com/wtsi-hgi/python-baton-wrapper/issues/44))

## 1.0.0 - 2016-06-14
### Changed
- Representation of user used in access control ([#32](https://github.com/wtsi-hgi/python-baton-wrapper/issues/32)).
- Use of hgijson and hgicommon from PyPI.
- Type of exception raised when baton encounters an unknown exception ([#34](https://github.com/wtsi-hgi/python-baton-wrapper/issues/34)).

### Added
- Ability to recursively change access controls.
- Setup for PyPI.

### Removed
- Redundant helper scripts.
- `get_all` method from `DataObjectReplicaCollection`.


## 0.5.0 - 2016-05-05
### Added
- First stable release

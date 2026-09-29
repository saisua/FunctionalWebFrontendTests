from __future__ import annotations
from typing import Any, TypeVar
from dataclasses import dataclass, field


Fwd = TypeVar("Fwd")


class ViewForwardRef:
	owner: type | None
	var_name: str

	_static_owner_fwd_ref: list = list()
	_cache_resolution: bool = True

	def __init__(self, owner: type | None, var_name: str):
		self.var_name = var_name
		self.owner = owner

	@staticmethod
	def try_resolve(
		fwd: Fwd | ViewForwardRef,
		new_owner: type | None = None
	) -> Fwd | Any:
		if not isinstance(fwd, ViewForwardRef) or (new_owner is None and fwd.owner is None):
			return fwd
		if new_owner is None or new_owner is fwd.owner:
			return fwd.resolve()

		prev_owner = fwd.owner
		if new_owner is not None:
			fwd.owner = new_owner

		result = fwd.resolve(raise_exc=False)
		if result is not AttributeError:
			return result

		print("#####", fwd, hasattr(fwd.owner, '__outer_owner__') and fwd.owner.__outer_owner__)

		seen_owners = {fwd.owner}
		while result is AttributeError and hasattr(fwd.owner, '__outer_owner__'):
			fwd.owner = fwd.owner.__outer_owner__

			if fwd.owner in seen_owners:
				break
			seen_owners.add(fwd.owner)

			result = fwd.resolve(raise_exc=False)

		if result is not AttributeError:
			return result

		if prev_owner is not None and prev_owner is not new_owner:
			fwd.owner = prev_owner

			result = fwd.resolve(raise_exc=False)

		if result is AttributeError:
			raise AttributeError(f"Attribute {fwd.var_name!r} was not found in {prev_owner} nor {new_owner}")
		return result
		

	def resolve(self, *, raise_exc: bool = True):
		print(f"Resolving {self}")
		owner = self.owner
		while owner is not None:
			# value = getattr(owner, self.var_name)
			# print('...', owner, value, type(value), isinstance(value, ViewForwardRef))
			if (
				(value := getattr(owner, self.var_name, None)) is not None and
				not isinstance(value, ViewForwardRef)
			):
				return value
			owner = getattr(owner, "__outer_owner__", None)

		print("Failed", self.owner, type(self.owner), isinstance(self.owner, type), hasattr(self.owner, '_obj_ref'))
		if (
			isinstance(self.owner, type) and
			hasattr(self.owner, '_obj_ref')
		):
			print(f"Resolved {self.var_name} owner class to {self.owner._obj_ref}")
			self.owner = self.owner._obj_ref
			return self.resolve()
		if raise_exc:
			raise AttributeError(f"Attribute {self.var_name!r} was not found in {self.owner}")
		return AttributeError

	def __repr__(self) -> str:
		return f"<ForwardRef {self.var_name!r} of {self.owner!r}>"

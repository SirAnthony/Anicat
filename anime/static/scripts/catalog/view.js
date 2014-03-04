/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * View builder module
 *
 */

define(['base/ajax', 'base/request_processor'],
function (ajax, RequestProcessor) {

	function Class(prototype, Parent) {
		Parent = Parent || Object
		var Child = function (options) {
			options = options || {}
			for (var x in options)
				this[x] = options[x]
			this._init.apply(this, Array.prototype.slice.call(arguments, 1))
			return this
		}
		Child.prototype = Object.create(Parent.prototype)
		Child.prototype.constructor = Child

		for (var x in prototype)
			if (prototype.hasOwnProperty(x))
				Child.prototype[x] = prototype[x]

		Child.prototype.super = function (propName) {
			var prop = Parent.prototype[propName]
			if (typeof prop !== "function")
				return prop
			var self = this
			return function() {
				var selfPrototype = self.constructor.prototype
				var pp = Parent.prototype
				for (var x in pp)
					self[x] = pp[x]
				try {
					return prop.apply(self, arguments);
				} finally {
					for (var x in selfPrototype)
						self[x] = selfPrototype[x]
				}
			}
		}
		return Child
	}

	var Base = Class({
		_init: function(processor) {
			if (processor instanceof RequestProcessor)
				this.processor = processor
			else if (isHash(processor))
				this.processor = new RequestProcessor(processor, this)
		},
		create: function() {},
		load: function(params) {
			ajax.load(this.link, params, this.processor)
			return false;
		}
	})

	return function(methods) {
		return Class(methods, Base)
	}
})
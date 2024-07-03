/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";

class SystrayIcon extends Component {
  setup() {
    super.setup(...arguments);
    this.action = useService("action");
    this.pageLocked = false; // Track whether the page is locked or not
  }

  _onClick(ev) {
    ev.stopPropagation(); // Prevent the click event from propagating
    this.pageLocked = !this.pageLocked; // Toggle the lock status
    this._updatePageLockStyle();
  }

  _updatePageLockStyle() {
    const blurAmount = this.pageLocked ? '5px' : '0'; // Adjust the blur amount based on lock status
    const pointerEvents = this.pageLocked ? 'none' : 'auto'; // Disable pointer events on the body when locked

    // Apply blur to the entire body
    document.body.style.filter = `blur(${blurAmount})`;
    document.body.style.pointerEvents = pointerEvents;

    // Exclude elements with the 'new_icon' class from the blur
    const newIconElements = document.querySelectorAll('.new_icon');
    for (const element of newIconElements) {
      element.style.filter = `blur(0)`;
      element.style.pointerEvents = 'auto';
    }
  }
}

SystrayIcon.template = "systray_icon";

export const systrayItem = { Component: SystrayIcon };

registry.category("systray").add("SystrayIcon", systrayItem, { sequence: 50 });
// ODC-ENC — parametric enclosure for ODC-REC-RPI-1A
// OpenSCAD — MIT with OpenDashCAN repo
// Units: mm

inner_l = 90;
inner_w = 60;
inner_h = 30;
wall = 2.0;
lid_h = 2.5;
corner_r = 4;
cable_od = 6.5; // OBD pigtail gland hole

module rounded_box(l, w, h, r) {
  hull() {
    for (x = [r, l - r])
      for (y = [r, w - r])
        translate([x, y, 0])
          cylinder(h = h, r = r, $fn = 32);
  }
}

module shell() {
  difference() {
    rounded_box(inner_l + 2 * wall, inner_w + 2 * wall, inner_h + wall, corner_r);
    translate([wall, wall, wall])
      rounded_box(inner_l, inner_w, inner_h + 1, corner_r - 1);
    // cable exit
    translate([-1, (inner_w + 2 * wall) / 2, wall + inner_h / 2])
      rotate([0, 90, 0])
        cylinder(h = wall + 2, d = cable_od, $fn = 32);
  }
}

module lid() {
  difference() {
    rounded_box(inner_l + 2 * wall, inner_w + 2 * wall, lid_h, corner_r);
    // label recess
    translate([wall + 8, wall + 8, lid_h - 0.6])
      cube([inner_l - 16, 18, 1]);
  }
}

shell();
translate([0, inner_w + 20, 0]) lid();

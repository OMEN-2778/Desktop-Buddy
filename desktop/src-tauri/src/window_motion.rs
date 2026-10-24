/// Both cursor and window coordinates are physical desktop pixels. In
/// particular, negative positions are valid with transparent popup headroom
/// and on monitors placed above or to the left of the primary display.
pub fn drag_position(origin: (i32, i32), cursor_origin: (f64, f64), cursor_now: (f64, f64)) -> (i32, i32) {
    (
        origin.0.saturating_add((cursor_now.0 - cursor_origin.0).round() as i32),
        origin.1.saturating_add((cursor_now.1 - cursor_origin.1).round() as i32),
    )
}

#[cfg(test)]
mod tests {
    use super::drag_position;

    #[test]
    fn oversized_window_can_move_vertically_beyond_work_area() {
        assert_eq!(drag_position((120, -700), (300.0, 200.0), (300.0, 60.0)), (120, -840));
        assert_eq!(drag_position((120, -700), (300.0, 200.0), (300.0, 450.0)), (120, -450));
    }

    #[test]
    fn moves_on_both_axes_and_negative_monitor_coordinates() {
        assert_eq!(drag_position((-1800, -450), (-1600.0, -200.0), (-1700.0, -350.0)), (-1900, -600));
        assert_eq!(drag_position((100, 200), (400.0, 500.0), (650.0, 500.0)), (350, 200));
    }

    #[test]
    fn physical_delta_is_not_scaled_again_or_accumulated() {
        for _zoom in [0.25, 0.50, 0.75, 1.0] {
            assert_eq!(drag_position((100, -500), (120.25, 250.5), (270.25, 325.5)), (250, -425));
            assert_eq!(drag_position((100, -500), (120.25, 250.5), (120.25, 250.5)), (100, -500));
        }
    }
}

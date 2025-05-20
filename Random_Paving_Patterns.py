# =============================================================================
# Author       : Studio Clue
# Created Date : 2025-05-20
# Description  : 
"""
Smart Panel(Paving Pattern) Generator for Rhino + Python
---------------------------------------------------------
This script creates vertically stacked panels (tiles) in columns,
using fixed height groups and random placement logic. Each panel
is assigned to a layer based on its height, with randomized colors
for visual organization.

The top of all columns is aligned by intelligently filling the gaps
with existing panel sizes when possible, and generating custom panels
only when needed.

Great for learning procedural geometry, layer management, and RhinoScriptSyntax.
"""
# =============================================================================

import rhinoscriptsyntax as rs
import Rhino.Geometry as geo
import random

def pavPattern(xNum, yNum):
    srfs = []
    y_bases = [0.0 for _ in range(xNum)]
    existing_layers = []

    bucket_size = 0.5
    max_r = 3.0
    num_buckets = int((max_r - 0.5) / bucket_size) + 1

    # Predefine exact heights for each bucket index
    bucket_heights = {i + 1: 0.5 + i * bucket_size for i in range(num_buckets)}
    height_values = sorted(bucket_heights.values(), reverse=True)  # For largest-to-smallest matching

    # Step 1: Generate regular tiles
    for n in range(yNum):
        for i in range(xNum):
            bucket_index = random.randint(1, num_buckets)
            r = bucket_heights[bucket_index]

            layer_name = "Height_Group_" + str(bucket_index)

            if not rs.IsLayer(layer_name):
                rs.AddLayer(layer_name)
                r_color = random.randint(0, 255)
                g_color = random.randint(0, 255)
                b_color = random.randint(0, 255)
                rs.LayerColor(layer_name, (r_color, g_color, b_color))
                existing_layers.append(layer_name)
            elif layer_name not in existing_layers:
                existing_layers.append(layer_name)

            y0 = y_bases[i]
            y1 = y0 + r

            x_vals = [i - 0.5, i - 0.5, i + 0.5, i + 0.5]
            y_vals = [y1, y0, y0, y1]
            pts = [geo.Point3d(x_vals[j], y_vals[j], 0) for j in range(4)]

            srf = rs.AddSrfPt([rs.coerce3dpoint(p) for p in pts])
            if srf:
                rs.ObjectLayer(srf, layer_name)

            y_bases[i] = y1
            srfs.append(srf)

    # Step 2: Fill top gap per column with smart + randomized logic
    max_height = max(y_bases)

    for i in range(xNum):
        current_y = y_bases[i]
        gap = max_height - current_y

        while gap > 0.001:
            # Find all valid panel sizes that can fit the current gap
            valid_fits = [(index, h) for index, h in bucket_heights.items() if h <= gap + 1e-6]

            if valid_fits:
                bucket_index, h = random.choice(valid_fits)

                # Check if this is the last tile that completes the column
                is_last_tile = abs(gap - h) < 1e-6

                y0 = current_y
                y1 = y0 + h
                x_vals = [i - 0.5, i - 0.5, i + 0.5, i + 0.5]
                y_vals = [y1, y0, y0, y1]
                pts = [geo.Point3d(x_vals[j], y_vals[j], 0) for j in range(4)]

                srf = rs.AddSrfPt([rs.coerce3dpoint(p) for p in pts])
                if srf:
                    if is_last_tile:
                        # Override the layer with a random one for variation
                        layer_name = random.choice(existing_layers)
                    else:
                        layer_name = "Height_Group_" + str(bucket_index)

                    rs.ObjectLayer(srf, layer_name)
                    srfs.append(srf)

                current_y = y1
                gap = max_height - current_y
            else:
                # Fallback case for tiny unmatched remainder
                h = gap
                y0 = current_y
                y1 = y0 + h
                layer_name = random.choice(existing_layers)
                x_vals = [i - 0.5, i - 0.5, i + 0.5, i + 0.5]
                y_vals = [y1, y0, y0, y1]
                pts = [geo.Point3d(x_vals[j], y_vals[j], 0) for j in range(4)]
                srf = rs.AddSrfPt([rs.coerce3dpoint(p) for p in pts])
                if srf:
                    rs.ObjectLayer(srf, layer_name)
                    srfs.append(srf)
                break

        # If a tiny remainder is left, fill it with a random custom panel
        if gap >= 0.001:
            y0 = current_y
            y1 = y0 + gap
            filler_layer = random.choice(existing_layers)
            x_vals = [i - 0.5, i - 0.5, i + 0.5, i + 0.5]
            y_vals = [y1, y0, y0, y1]
            pts = [geo.Point3d(x_vals[j], y_vals[j], 0) for j in range(4)]
            srf = rs.AddSrfPt([rs.coerce3dpoint(p) for p in pts])
            if srf:
                rs.ObjectLayer(srf, filler_layer)
                srfs.append(srf)

    return srfs

# Run the tile generator
pavPattern(10, 30)
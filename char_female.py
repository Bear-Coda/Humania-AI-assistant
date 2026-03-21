import time, math
from PIL import Image

WIDTH = 100 

def get_frame(img_data, is_talking=False, idle_time=0, is_smiling=False):
    chars = "@#%*+      "
    t = time.time()
    
    speed = 0.16 if is_talking else 0.05
    sway_y = math.cos(t * (speed * 0.9)) * (1.2 if is_talking else 0.5)
    sway_x = (math.sin(t * speed) * (2.0 if is_talking else 0.8))
    
    w, h = img_data.size
    new_width = WIDTH
    new_height = int((h / w) * new_width * 0.36)

    # --- COORDINATES (Mouth shifted UP to 0.58) ---
    m_y_c = int(new_height * 0.58)
    e_y_c = int(new_height * 0.38)
    e_l_x, e_r_x = int(new_width * 0.22), int(new_width * 0.52) 
    e_w = int(new_width * 0.12)

    mouth_open = math.sqrt(abs(math.sin(t * 8.5))) if is_talking else 0.05
    eye_open = 0.6 + 0.3 * math.sin(t * 1.1)
    look_x = math.sin(t * 0.85)
    look_y = math.cos(t * 0.45) * 0.3

    ascii_frame = []
    for y in range(new_height):
        line = ""
        pivot_inf = math.pow(max(0, min(1, (y - (new_height * 0.98)) / -(new_height * 0.85))), 2.0)
        
        for x in range(new_width):
            orig_x = max(0, min(w - 1, int(((x + (sway_x * pivot_inf)) / new_width) * w)))
            orig_y = max(0, min(h - 1, int(((y - (sway_y * pivot_inf)) / new_height) * h)))
            
            sample_y = orig_y
            is_void = False
            char_override = None

            # --- EYES ---
            if (e_l_x < x < e_l_x + e_w) or (e_r_x < x < e_r_x + e_w):
                ex_s = e_l_x if x < e_r_x else e_r_x
                e_t = math.pow(math.cos(abs((x - (ex_s + e_w/2)) / (e_w/2)) * (math.pi / 2)), 1.2)
                dist_e = abs(y - e_y_c)
                
                if dist_e < (new_height * 0.05) * e_t:
                    e_shift = (-1 if y < e_y_c else 1) * eye_open * 4.5 * (((new_height * 0.05) * e_t - dist_e) / ((new_height * 0.05) * e_t)) * e_t
                    sample_y = max(0, min(h - 1, int(orig_y + e_shift)))
                    
                    if eye_open > 0.1 and dist_e < ((new_height * 0.05) * e_t * eye_open * 0.8):
                        is_void = True
                        if math.sqrt((y - (e_y_c + look_y))**2 + (x - ((ex_s + e_w/2) + look_x))**2) < 1.2:
                            char_override = "█"

            # --- MOUTH (Shifted LEFT to 0.40 and WIDER range) ---
            if (new_width * 0.23 < x < new_width * 0.57):
                m_h = abs((x - (new_width * 0.40)) / (new_width * 0.17))
                m_t = math.cos(max(-1.5, min(1.5, m_h * (math.pi / 2))))
                dist_m = abs(y - m_y_c)
                
                if dist_m < (new_height * 0.06) * m_t:
                    m_s = (-1 if y < m_y_c else 1) * mouth_open * 8.0 * (((new_height * 0.06) * m_t - dist_m) / ((new_height * 0.06) * m_t)) * m_t
                    sample_y = max(0, min(h - 1, int(orig_y + m_s)))
                    
                    if mouth_open > 0.4 and dist_m < ((new_height * 0.06) * m_t * mouth_open * 0.6):
                        is_void = True

            if char_override: line += char_override
            elif is_void: line += " "
            else:
                pixel = img_data.getpixel((orig_x, max(0, min(h-1, int(sample_y)))))
                val = pixel[0] if isinstance(pixel, tuple) else pixel
                line += chars[min(val // 26, 9)]
                
        ascii_frame.append(line)
    return "\n".join(ascii_frame)
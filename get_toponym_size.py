def get_toponym_size(toponym):
    corners = toponym["boundedBy"]["Envelope"]
    lower_corner = corners["lowerCorner"].split()
    upper_corner = corners["upperCorner"].split()
    return (abs(float(lower_corner[0]) - float(upper_corner[0])),
            abs(float(lower_corner[1]) - float(upper_corner[1])))

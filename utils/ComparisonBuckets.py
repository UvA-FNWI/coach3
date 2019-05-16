def frequency_count_comp(grades, user_grade, nr_bins=18, minn=1.0, maxx=10.0):
    " Creates bins for histogram plot of grades. Finds correct student assignment."

    ret = []
    data = []
    binsize = (maxx - minn) / float(nr_bins)
    student_bucket = []
    # construct bins
    # each bin consist of a start position and end position and a zero value(?)
    # QUESTION: why the null value?
    # each bin represents a grade on the x-axis
    # bins are stored in the ret variable
    for x in range(0, nr_bins):
        start = minn + x * binsize
        ret.append([start-0.25, start+0.24, 0])
        data.append({'bucket': start, 'size': 0})
        # QUESTION: why do we need the ret array?
    # assign items to bin
    for item in grades:
        for i, binn in enumerate(ret):
            if item is not None and binn[0] <= item < binn[1]:
                    data[i]['size'] += 1
            # sets aside the student grade in another student_bucket
            # NOTE: the student grade is still included in the general bucket
            # as it will be included in the average grade calculation
            if binn[0] <= user_grade < binn[1]:
                student_bucket = data[i]['bucket']
                data[i]['size'] -= 1

    data.append({'assignment': student_bucket})
    return data
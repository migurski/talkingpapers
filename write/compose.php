<?php

    ini_set('include_path', ini_get('include_path').PATH_SEPARATOR.'/usr/share/pear');

    require_once 'FPDF/fpdf.php';
    require_once 'HTTP/Request.php';

    function annotate_pdf(&$pdf, $print_url)
    {
        $icon_filename = realpath(dirname(__FILE__).'/../read/GMDH02_00364.png');
        $pdf->image($icon_filename, 0, 0, 144, 144);
        
        $icon_filename = realpath(dirname(__FILE__).'/../read/GMDH02_00647.png');
        $pdf->image($icon_filename, 0, 648, 122, 144);
        
        $pdf->setFont('Helvetica', 'B', 36);
        $pdf->text(114, 82, 'Talking Papers');
        
        $size = 72;
        $pad = 8;
        
        $pdf->setFillColor(0xFF);
        $pdf->rect($pdf->w - 36 - $size - $pad, $pdf->h - 36 - $size - $pad, $size + $pad * 2, $size + $pad * 2, 'F');

        $req = new HTTP_Request('http://chart.apis.google.com/chart?chs=264x264&cht=qr&chld=Q|0');
        $req->addQueryString('chl', $print_url);
        echo $req->getURL()."\n";
        $res = $req->sendRequest();
        
        if(PEAR::isError($res))
            die_with_code(500, "{$res->message}\n{$q}\n");
        
        $code_img = imagecreatefromstring($req->getResponseBody());
        $code_filename = tempnam(TMP_DIR, 'composed-code-');
        imagepng($code_img, $code_filename);
        $pdf->image($code_filename, $pdf->w - 36 - $size, $pdf->h - 36 - $size, $size, $size, 'png');
        
        unlink($code_filename);
    }

    $pdf = new FPDF('P', 'pt', 'letter');
    $pdf->addPage();
    
    annotate_pdf($pdf, 'http://github.com/migurski/talkingpapers/network');

   /**
    * Form fields, loosely based on HTML5 input element spec.,
    * http://www.w3.org/TR/html5/forms.html#the-input-element
    */
    $fields = array(array('name' => 'Last', 'type' => 'text', 'size' => 30),
                    array('name' => 'First', 'type' => 'text', 'size' => 30),
                    array('name' => 'Date Of Birth', 'type' => 'date'),
                    array('name' => 'Nationality', 'type' => 'text'));
    
    $y = 144;
    
    function draw_text_box(&$pdf, $x, $y, $size, $subtext=false)
    {
        // width, height, right, bottom
        $c = 18;
        $w = $size * $c;
        $h = 18;
        $r = $x + $w;
        $b = $y + $h;

        $pdf->setDrawColor(0x00);
        $pdf->setFont('Helvetica', 'I', 6);

        // outline
        $pdf->setLineWidth(.5);
        $pdf->rect($x, $y, $w, $h, 'D');
        
        // ticks
        for($o = $x + $c; $o < $r; $o += $c)
            $pdf->line($o, $b, $o, $b - 4);

        // thick underline
        $pdf->setLineWidth(1.5);
        $pdf->line($x + .75, $b - .75, $r - .75, $b - .75);

        // optional subtext
        if($subtext)
            $pdf->text($x + 2, $b + 6, $subtext);
    }
    
    foreach($fields as $field)
    {
        $x = 36;
        
        $pdf->setFont('Helvetica', 'B', 12);
        $pdf->text($x, $y, $field['name']);
        
        $y += 6;
        
        switch($field['type'])
        {
            case 'text':
                $size = $field['size'] ? $field['size'] : 20;
                draw_text_box($pdf, $x, $y, $size);
                break;

            case 'date':
                $pdf->setFont('Helvetica', 'I', 6);
                draw_text_box($pdf, $x, $y, 4, 'year');
                draw_text_box($pdf, $x + 78, $y, 2, 'month');
                draw_text_box($pdf, $x + 120, $y, 2, 'day');
                break;
        }
        
        $y += 48;
    }
    
    $pdf->output('out.pdf', 'F');

?>
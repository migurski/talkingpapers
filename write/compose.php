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
    $pdf->output('out.pdf', 'F');

?>
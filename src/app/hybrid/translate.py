# -*- coding: utf-8 -*-
import argparse
import fileinput

from mt.hybrid import SimpleWsdTriangleTranslator, SimpleTriangleTranslator

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Run translate engine on a file")
    parser.add_argument('--moses')
    parser.add_argument('--lucy')
    parser.add_argument('--lcm')
    parser.add_argument('--wsd')
    parser.add_argument('--model')
    parser.add_argument('--srclang')
    parser.add_argument('--tgtlang')
    parser.add_argument('--config', nargs='+', action='append')
    parser.add_argument('--reverse', dest='reverse', action='store_true')
    parser.add_argument('--input')
    parser.add_argument('--output')
    parser.add_argument('--output_verbose')
    args = parser.parse_args()

    if args.wsd:
        hybridsystem = SimpleWsdTriangleTranslator(moses_url=args.moses,
                                     lucy_url=args.lucy,
                                     lcm_url=args.lcm,
                                     wsd_url=args.wsd,
                                     source_language=args.srclang,
                                     target_language=args.tgtlang,
                                     classifiername=args.model,
                                     configfilenames=args.config,
                                     reverse=args.reverse
                                     )
    else:
        hybridsystem = SimpleTriangleTranslator(moses_url=args.moses,
                                     lucy_url=args.lucy,
                                     lcm_url=args.lcm,
                                     source_language=args.srclang,
                                     target_language=args.tgtlang,
                                     classifiername=args.model,
                                     configfilenames=args.config,
                                     reverse=args.reverse
                                     )

    output_file = open(args.output, 'w')
    verbose_file = open(args.output_verbose, 'w')
    for line in open(args.input):
        translated_line, description = hybridsystem.translate(line)
        print >>output_file, translated_line
        print >>verbose_file, description
    output_file.close()
    verbose_file.close()

#!/bin/bash
cd spf
celery -A spf worker -l INFO

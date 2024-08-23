begonia_desc_dwca_url=https://files.worldfloraonline.org/files/Begonia/Begonia_WFO_content_Wed-Mar-2024_14_28_32.zip
begonia_taxa_dwca_url=https://files.worldfloraonline.org/files/WFO_Backbone/Begoniaceae/Begoniaceae.zip
solanaceae_desc_dwca_url=https://files.worldfloraonline.org/files/Solanaceae/WFO/Solanaceae.zip
solanaceae_taxa_dwca_url=https://files.worldfloraonline.org/files/Solanaceae/WFO/Solanaceae.zip

wget_options=--no-check-certificate --quiet

downloads/%.zip: 
	mkdir -p downloads
	wget ${wget_options} -O $@ ${$*_dwca_url}

data/%-taxa.txt: scripts/init/dwca2csv.py downloads/%_taxa.zip
	mkdir -p data
	python $^ --output_type=core $@

data/%-desc.txt: scripts/init/dwca2csv.py downloads/%_desc.zip
	mkdir -p data
	python $^ --output_type=desc $@

taxa: data/begonia-taxa.txt data/solanaceae-taxa.txt
desc: data/begonia-desc.txt data/solanaceae-desc.txt

all: data/begonia-taxa.txt data/begonia-desc.txt data/solanaceae-taxa.txt data/solanaceae-desc.txt

clean:
	rm -rf data

sterilise:
	rm -rf data downloads

.PRECIOUS: downloads/begonia_desc.zip downloads/begonia_taxa.zip downloads/solanaceae_desc.zip downloads/solanaceae_taxa.zip
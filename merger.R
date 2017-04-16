args <- commandArgs(trailingOnly = TRUE)
input_file = args[1]
out_file = args[2]
files_to_merge = unlist(strsplit(args[3],','))

#print(input_file)
#print(output_file)
#print(merge_files)

init_header = read.csv(input_file,sep="\t",header=T)
init_header = read.csv(pipe(paste("cut -f3-8,10,11",input_file)),header=F,sep="\t",stringsAsFactors=F,comment.char="",
                    #col.names=c('ID','POS','END','REF_ANNO','ALT_ANNO','CHROM','REF','ALT_VCF'),
                    #colClasses=c('numeric','numeric','numeric','character','character','character','character','character'),
                    col.names=c('END','REF_ANNO','ALT_ANNO','ID','CHROM','POS','REF','ALT_VCF'),
                    colClasses=c('numeric','character','character','numeric','character','numeric','character','character'),
                   )
write.table(
      Reduce(
	function(x,y) {
	  df = read.csv(y, sep="\t",comment.char="")
	  df$ID = as.numeric(df$ID)
	  return(merge(x,df,all=T,by=('ID')))
	},
	files_to_merge,
	init = init_header
      ),
out_file,
sep="\t",
row.names=F,
col.names=T,
quote=F,
)

#ab <- rbind(args[1], args[2])
#colFun <- function(x){x[which(!is.na(x))]}
#ddply(ab,.(id),function(x){colwise(colFun)(x)})
